"""
admin.py — Admin Dashboard Routes for CampusAid
"""

from flask import request, jsonify, render_template, Response, stream_with_context
from PyPDF2 import PdfReader
from docx import Document
import json
import os
import time


def register_admin_routes(app, client, COLLEGES, SYSTEM_PROMPTS, build_system_prompt, load_all_colleges):
    """Registers all admin-related routes with the Flask app."""

    # ─────────────────────────────────────────
    # ADMIN DASHBOARD HOME
    # ─────────────────────────────────────────

    @app.route("/admin/<college_id>")
    def admin_dashboard(college_id):
        if college_id not in COLLEGES:
            return "College not found", 404
        college_data = COLLEGES[college_id]
        return render_template("admin.html", college=college_data)


    # ─────────────────────────────────────────
    # EXTRACT TEXT FROM PDF/DOCX/TXT
    # ─────────────────────────────────────────

    def extract_text_from_file(file):
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()

        elif filename.endswith(".docx"):
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text.strip()

        elif filename.endswith(".txt"):
            return file.read().decode("utf-8").strip()

        else:
            return None


    # ─────────────────────────────────────────
    # EXTRACT POLICIES FROM A SINGLE CHUNK
    # ─────────────────────────────────────────

    def extract_chunk(chunk_text, chunk_num, total_chunks):
        extraction_prompt = f"""You are a policy extraction AI for college handbooks.

This is chunk {chunk_num} of {total_chunks} from a college document.

Your job: Extract every policy/rule from the text below into structured JSON.

CATEGORIES (use these EXACT names):
- academic (exams, attendance, grading, integrity, plagiarism)
- financial (fees, scholarships, deferrals, refunds)
- administrative (hostel, grievances, contacts, procedures)
- emotional (mental health, counseling, support services)

OUTPUT FORMAT (return ONLY valid JSON):
{{
  "extracted_policies": [
    {{
      "title": "Short policy title",
      "category": "academic",
      "rules": [
        "Clear rule statement.",
        "Another rule."
      ]
    }}
  ]
}}

RULES:
1. Extract EVERY policy in this chunk.
2. Each rule must be a complete sentence.
3. Use ONLY the 4 categories above.
4. Default to "administrative" if unsure.
5. Return ONLY JSON. No markdown. No explanation.
6. If no policies found, return: {{"extracted_policies": []}}
"""

        ai_response = ""
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": f"Extract policies from this text:\n\n{chunk_text}"}
                ],
                model="llama-3.1-8b-instant",
                max_tokens=2000,
                temperature=0.1
            )

            ai_response = response.choices[0].message.content.strip()

            if "```" in ai_response:
                parts = ai_response.split("```")
                if len(parts) >= 2:
                    ai_response = parts[1]
                    if ai_response.startswith("json"):
                        ai_response = ai_response[4:]
            ai_response = ai_response.strip()

            start = ai_response.find("{")
            end = ai_response.rfind("}")
            if start != -1 and end != -1:
                ai_response = ai_response[start:end+1]

            extracted = json.loads(ai_response)
            return extracted.get("extracted_policies", [])

        except json.JSONDecodeError as e:
            print(f"JSON parse error in chunk: {e}")
            print(f"Response was: {ai_response[:300]}")
            return []
        except Exception as e:
            print(f"Chunk extraction error: {e}")
            return []


    # ─────────────────────────────────────────
    # STREAMING UPLOAD ENDPOINT
    # ─────────────────────────────────────────

    @app.route("/admin/<college_id>/upload_document", methods=["POST"])
    def admin_upload_document(college_id):
        if college_id not in COLLEGES:
            return jsonify({"status": "error", "message": "College not found"}), 404

        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"status": "error", "message": "No file selected"}), 400

        allowed = file.filename.lower().endswith((".pdf", ".docx", ".txt"))
        if not allowed:
            return jsonify({"status": "error", "message": "Only PDF, DOCX, or TXT files supported"}), 400

        try:
            text = extract_text_from_file(file)
            if not text:
                return jsonify({"status": "error", "message": "Could not extract text from file"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

        filename = file.filename

        def generate():
            yield f"data: {json.dumps({'type': 'start', 'message': 'Reading document...', 'length': len(text)})}\n\n"

            CHUNK_SIZE = 3000
            chunks = []

            if "\n\n" in text:
                paragraphs = text.split("\n\n")
            else:
                paragraphs = text.split("\n")

            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < CHUNK_SIZE:
                    current_chunk += para + "\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n"
            if current_chunk:
                chunks.append(current_chunk.strip())

            final_chunks = []
            for chunk in chunks:
                if len(chunk) <= CHUNK_SIZE:
                    final_chunks.append(chunk)
                else:
                    for i in range(0, len(chunk), CHUNK_SIZE):
                        final_chunks.append(chunk[i:i + CHUNK_SIZE])
            chunks = final_chunks

            total_chunks = len(chunks)
            yield f"data: {json.dumps({'type': 'chunking', 'total_chunks': total_chunks})}\n\n"

            all_policies = []

            for i, chunk in enumerate(chunks):
                current_num = i + 1

                yield f"data: {json.dumps({'type': 'processing', 'current': current_num, 'total': total_chunks, 'policies_so_far': len(all_policies)})}\n\n"

                chunk_policies = extract_chunk(chunk, current_num, total_chunks)
                if chunk_policies:
                    all_policies.extend(chunk_policies)

                yield f"data: {json.dumps({'type': 'chunk_done', 'current': current_num, 'total': total_chunks, 'policies_so_far': len(all_policies), 'found_in_chunk': len(chunk_policies)})}\n\n"

                if i < total_chunks - 1:
                    yield f"data: {json.dumps({'type': 'waiting', 'current': current_num, 'total': total_chunks, 'policies_so_far': len(all_policies)})}\n\n"
                    time.sleep(12)

            yield f"data: {json.dumps({'type': 'complete', 'filename': filename, 'policy_count': len(all_policies), 'extracted_policies': all_policies})}\n\n"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")


    # ─────────────────────────────────────────
    # SAVE APPROVED POLICIES
    # ─────────────────────────────────────────

    @app.route("/admin/<college_id>/save_policies", methods=["POST"])
    def admin_save_policies(college_id):
        if college_id not in COLLEGES:
            return jsonify({"status": "error", "message": "College not found"}), 404

        data = request.json
        new_policies = data.get("policies", [])

        if not new_policies:
            return jsonify({"status": "error", "message": "No policies to save"}), 400

        try:
            college_file = f"colleges/{college_id}.json"
            with open(college_file, "r", encoding="utf-8") as f:
                college_data = json.load(f)

            existing_policies = college_data.get("policies", {})

            # Build a set of existing titles (lowercased for comparison)
            existing_titles = {p["title"].lower().strip() for p in existing_policies.values()}

            added_count = 0
            skipped_count = 0
            added_titles = []
            skipped_titles = []

            for policy in new_policies:
                policy_title_lower = policy["title"].lower().strip()

                # Check if this policy title already exists
                if policy_title_lower in existing_titles:
                    skipped_count += 1
                    skipped_titles.append(policy["title"])
                    continue

                # New policy — add it
                base_key = policy["title"].lower().replace(" ", "_").replace("/", "_")
                key = base_key
                counter = 1

                while key in existing_policies:
                    key = f"{base_key}_{counter}"
                    counter += 1

                existing_policies[key] = {
                    "title": policy["title"],
                    "category": policy["category"],
                    "rules": policy["rules"]
                }
                existing_titles.add(policy_title_lower)
                added_count += 1
                added_titles.append(policy["title"])

            college_data["policies"] = existing_policies

            # Only save to disk if we actually added something
            if added_count > 0:
                with open(college_file, "w", encoding="utf-8") as f:
                    json.dump(college_data, f, indent=2, ensure_ascii=False)

                COLLEGES[college_id] = college_data
                SYSTEM_PROMPTS[college_id] = build_system_prompt(college_data)

            # Build a clear message based on what happened
            if added_count == 0 and skipped_count > 0:
                message = f"All {skipped_count} policies already exist in {college_data['name']}. Nothing new to add."
                status = "info"
            elif added_count > 0 and skipped_count == 0:
                message = f"Added {added_count} new policies to {college_data['name']}."
                status = "success"
            else:
                message = f"Added {added_count} new policies, skipped {skipped_count} duplicates."
                status = "success"

            return jsonify({
                "status": status,
                "message": message,
                "added_count": added_count,
                "skipped_count": skipped_count,
                "added_titles": added_titles,
                "skipped_titles": skipped_titles,
                "total_policies": len(existing_policies)
            })

        except Exception as e:
            return jsonify({"status": "error", "message": f"Save error: {str(e)}"}), 500


    # ─────────────────────────────────────────
    # GET ALL POLICIES
    # ─────────────────────────────────────────

    @app.route("/admin/<college_id>/get_policies", methods=["GET"])
    def admin_get_policies(college_id):
        if college_id not in COLLEGES:
            return jsonify({"status": "error", "message": "College not found"}), 404

        college_data = COLLEGES[college_id]
        return jsonify({
            "status": "success",
            "college_name": college_data.get("name"),
            "policies": college_data.get("policies", {})
        })
    # ─────────────────────────────────────────
    # DELETE A POLICY
    # ─────────────────────────────────────────

    @app.route("/admin/<college_id>/delete_policy/<policy_key>", methods=["DELETE"])
    def admin_delete_policy(college_id, policy_key):
        if college_id not in COLLEGES:
            return jsonify({"status": "error", "message": "College not found"}), 404

        try:
            college_file = f"colleges/{college_id}.json"
            with open(college_file, "r", encoding="utf-8") as f:
                college_data = json.load(f)

            policies = college_data.get("policies", {})

            if policy_key not in policies:
                return jsonify({"status": "error", "message": "Policy not found"}), 404

            deleted_title = policies[policy_key]["title"]
            del policies[policy_key]

            college_data["policies"] = policies

            with open(college_file, "w", encoding="utf-8") as f:
                json.dump(college_data, f, indent=2, ensure_ascii=False)

            # Refresh in-memory data
            COLLEGES[college_id] = college_data
            SYSTEM_PROMPTS[college_id] = build_system_prompt(college_data)

            return jsonify({
                "status": "success",
                "message": f"Deleted '{deleted_title}'",
                "total_policies": len(policies)
            })

        except Exception as e:
            return jsonify({"status": "error", "message": f"Delete error: {str(e)}"}), 500

    return app