"""
test_app.py
===========
Threat Vector - Comprehensive Automated Test Suite
--------------------------------------------------
Verifies:
1. Unauthenticated route redirection to /login
2. Standard username/password login & session authentication
3. Main dashboard rendering & metrics
4. Continuous drill flow: starting drills, submitting verdicts, and advancing seamlessly via next_drill
5. Upgraded multi-modal AI Inspector with text & file upload and Threat Report generation
6. CTF flag submission and defense point awarding
7. War Room multi-phase incident progression
8. Leaderboard dynamic ranking and accuracy calculation
9. Profile analytics & weakness diagnostic generation
"""

import io
import unittest
from app import app
from database import init_db

class ThreatVectorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

    def setUp(self):
        self.client = app.test_client()
        # Clean user 1 test state for idempotent test runs
        from database import get_db_connection
        conn = get_db_connection()
        conn.execute("DELETE FROM ctf_submissions WHERE user_id = 1")
        conn.execute("DELETE FROM drill_responses WHERE user_id = 1")
        conn.execute("DELETE FROM war_room_logs WHERE user_id = 1")
        conn.execute("DELETE FROM knowledge_progress WHERE user_id = 1")
        conn.execute("DELETE FROM knowledge_attempts WHERE user_id = 1")
        conn.execute("DELETE FROM knowledge_active_sessions WHERE user_id = 1")
        conn.commit()
        conn.close()

    def test_01_unauthenticated_redirect(self):
        """Verify unauthenticated user is redirected to /login when accessing dashboard."""
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_02_standard_login(self):
        """Verify standard user authentication with username and password."""
        response = self.client.post("/login", data={
            "action": "login",
            "username": "cadet",
            "password": "password123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"THREAT VECTOR", response.data)
        self.assertIn(b"cadet", response.data)

    def test_03_dashboard_loads(self):
        """Verify dashboard displays metrics and core features."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"
        
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Defense Score", response.data)
        self.assertIn(b"Simulation Drills", response.data)
        self.assertIn(b"AI Threat Inspector", response.data)

    def test_04_continuous_drills_flow(self):
        """Verify drills load, accept answers, and continuous /drills/next advances without crashing."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        # 1. Access drills
        resp = self.client.get("/drills")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"SECURE-MAIL-CLIENT", resp.data)

        # 2. Submit drill answer
        submit_resp = self.client.post("/drills/submit", data={
            "scenario_id": 1,
            "verdict": 1,
            "indicators": ["Lookalike sender domain (micros0ft with zero)"]
        }, follow_redirects=True)
        self.assertEqual(submit_resp.status_code, 200)
        self.assertIn(b"CORRECT VERDICT ACQUIRED", submit_resp.data)
        self.assertIn(b"Next Drill", submit_resp.data)

        # 3. Continuous advance to next drill
        next_resp = self.client.get("/drills/next?current_id=1", follow_redirects=True)
        self.assertEqual(next_resp.status_code, 200)
        self.assertIn(b"DRILL", next_resp.data)

    def test_05_multi_modal_ai_inspector(self):
        """Verify AI Inspector classifies text AND processes uploaded document with Threat Report."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        # Test Text analysis
        mal_text = "Urgent: Your Microsoft 365 password expires in 2 hours. Verify at http://m365-verify.top/auth"
        resp_mal = self.client.post("/inspector", data={"inspect_text": mal_text})
        self.assertEqual(resp_mal.status_code, 200)
        self.assertIn(b"MALICIOUS THREAT", resp_mal.data)
        self.assertIn(b"Incident Assessment Report", resp_mal.data)
        self.assertIn(b"Extracted Indicators of Compromise", resp_mal.data)
        self.assertIn(b"Step-by-Step Professional Analyst Workflow", resp_mal.data)

        # Test File Upload multi-modal analysis (mock text telemetry file)
        test_file = (io.BytesIO(b"ATTENTION: Immediate account suspension. Wire funds to foreign account http://rogue-bank.xyz/pay"), "suspicious_memo.txt")
        resp_file = self.client.post("/inspector", data={
            "inspect_text": "",
            "inspect_file": test_file
        }, content_type="multipart/form-data")
        self.assertEqual(resp_file.status_code, 200)
        self.assertIn(b"MALICIOUS THREAT", resp_file.data)
        self.assertIn(b"suspicious_memo.txt", resp_file.data)

    def test_06_ctf_range(self):
        """Verify CTF page loads and correct flag capture awards points."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/ctf")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"SSH Brute Force Intrusion Detective", resp.data)

        # Submit correct flag for challenge 1
        flag_resp = self.client.post("/ctf/submit", data={
            "challenge_id": 1,
            "flag": "flag{192.168.1.105_sysadmin}"
        }, follow_redirects=True)
        self.assertEqual(flag_resp.status_code, 200)
        self.assertIn(b"FLAG CAPTURED", flag_resp.data)

    def test_07_war_room_progression(self):
        """Verify War Room loads incident and handles tactical decisions."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/war-room")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Operation BlackOut", resp.data)

        # Submit Phase 1 action
        choice_resp = self.client.post("/war-room/submit", data={
            "incident_id": 1,
            "phase_index": 0,
            "chosen_option": 0
        }, follow_redirects=True)
        self.assertEqual(choice_resp.status_code, 200)
        self.assertIn(b"Command executed", choice_resp.data)

    def test_08_leaderboard_and_profile(self):
        """Verify Leaderboard and Risk Profile pages render accurately."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        lb_resp = self.client.get("/leaderboard")
        self.assertEqual(lb_resp.status_code, 200)
        self.assertIn(b"Cybersecurity Defense Leaderboard", lb_resp.data)
        self.assertIn(b"Accuracy Rate", lb_resp.data)
        self.assertIn(b"cadet", lb_resp.data)

        prof_resp = self.client.get("/profile")
        self.assertEqual(prof_resp.status_code, 200)
        self.assertIn(b"Trainee Threat Analytics", prof_resp.data)
        self.assertIn(b"Certificate of Cybersecurity Defense Readiness", prof_resp.data)

    def test_09_defensive_null_checks(self):
        """Verify all protected routes safely redirect when unauthenticated or session has stale/null user."""
        protected_routes = ["/", "/dashboard", "/drills", "/drills/next", "/inspector", "/ctf", "/war-room", "/leaderboard", "/profile"]
        
        # 1. Unauthenticated requests must safely redirect without 500 error
        for route in protected_routes:
            resp = self.client.get(route, follow_redirects=False)
            self.assertEqual(resp.status_code, 302, f"Route {route} failed to redirect unauthenticated access")
            self.assertIn("/login", resp.headers["Location"])

        # 2. Stale or invalid session IDs (e.g. user deleted or user_id=999999) must not crash
        with self.client.session_transaction() as sess:
            sess["user_id"] = 999999
        for route in protected_routes:
            resp = self.client.get(route, follow_redirects=False)
            self.assertEqual(resp.status_code, 302, f"Route {route} crashed on stale session")
            self.assertIn("/login", resp.headers["Location"])

        # 3. Ensure /login loads cleanly without requiring an active session
        login_resp = self.client.get("/login")
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"Sign In", login_resp.data)

    def test_10_quick_demo_login(self):
        """Verify Quick Demo Login button on /login and successful 1-click authentication to /demo-login."""
        # 1. Login page contains Quick Demo Login button
        page_resp = self.client.get("/login")
        self.assertEqual(page_resp.status_code, 200)
        self.assertIn(b"Quick Demo Login as Cadet", page_resp.data)
        self.assertIn(b"/demo-login", page_resp.data)

        # 2. Submitting to /demo-login establishes session as cadet
        resp = self.client.post("/demo-login", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Authenticated as Analyst", resp.data)
        self.assertIn(b"cadet", resp.data)

    def test_11_war_room_navigation_wraparound(self):
        """Verify War Room completion navigates sequentially to next incident and wraps around."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        # Check Incident 1 completion links to Incident 2
        resp1 = self.client.get("/war-room?incident_id=1")
        self.assertEqual(resp1.status_code, 200)
        self.assertIn(b"incident_id=2", resp1.data)

        # Check Incident 2 completion links to Incident 3
        resp2 = self.client.get("/war-room?incident_id=2")
        self.assertEqual(resp2.status_code, 200)
        self.assertIn(b"incident_id=3", resp2.data)

        # Check Incident 3 (last incident) wraps around to Incident 1
        resp3 = self.client.get("/war-room?incident_id=3")
        self.assertEqual(resp3.status_code, 200)
        self.assertIn(b"incident_id=1", resp3.data)

    def test_12_profile_spear_phishing_category(self):
        """Verify Profile Threat Analytics explicitly includes Spear Phishing category."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/profile")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Spear Phishing", resp.data)

    def test_13_ml_model_offline_error_handling(self):
        """Verify inspector gracefully handles missing model without silent failure."""
        import app as tv_app
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        # Temporarily mock pipeline as None
        orig_pipeline = tv_app.ml_pipeline
        try:
            tv_app.ml_pipeline = None

            # Submitting text when model is offline flashes danger message
            resp = self.client.post("/inspector", data={"inspect_text": "Sample test message"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"AI Threat Inspector Offline", resp.data)

            # GET page shows warning banner
            get_resp = self.client.get("/inspector")
            self.assertEqual(get_resp.status_code, 200)
            self.assertIn(b"AI Classification Engine Notice", get_resp.data)
        finally:
            tv_app.ml_pipeline = orig_pipeline

    def test_14_knowledge_check_modules_overview(self):
        """Verify Knowledge Check modules overview loads all 8 modules and metrics."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/knowledge-check")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Knowledge Check System", resp.data)
        self.assertIn(b"MODULE 01", resp.data)
        self.assertIn(b"MODULE 08", resp.data)
        self.assertIn(b"Computer Fundamentals", resp.data)
        self.assertIn(b"Security Operations &amp; GRC", resp.data)

    def test_15_knowledge_check_difficulty_selection(self):
        """Verify difficulty selection displays Easy, Intermediate, and Hard tiers."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/knowledge-check/1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Computer Fundamentals", resp.data)
        self.assertIn(b"EASY LEVEL", resp.data)
        self.assertIn(b"INTERMEDIATE LEVEL", resp.data)
        self.assertIn(b"HARD LEVEL", resp.data)

    def test_16_knowledge_check_quiz_session_and_submission(self):
        """Verify quiz session runner initializes and accepts answer submissions."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        # 1. Start quiz
        resp = self.client.get("/knowledge-check/1/Easy")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"QUESTION 1 OF 20", resp.data)
        self.assertIn(b"Submit Answer", resp.data)

        # 2. Get active session ID from DB
        from database import get_db_connection
        conn = get_db_connection()
        row = conn.execute("SELECT session_id, questions_json FROM knowledge_active_sessions WHERE user_id = 1").fetchone()
        conn.close()
        self.assertIsNotNone(row)
        session_id = row["session_id"]
        import json
        questions = json.loads(row["questions_json"])
        q0 = questions[0]

        # 3. Submit answer to question 0
        submit_resp = self.client.post("/knowledge-check/submit", json={
            "session_id": session_id,
            "question_id": q0["id"],
            "selected": q0["correct"]
        })
        self.assertEqual(submit_resp.status_code, 200)
        res_data = submit_resp.get_json()
        self.assertEqual(res_data["status"], "success")
        self.assertTrue(res_data["is_correct"])
        self.assertIn("explanation", res_data)
        self.assertIn("why_correct", res_data["explanation"])

        # 4. Advance to next question
        next_resp = self.client.post("/knowledge-check/next", json={
            "session_id": session_id
        })
        self.assertEqual(next_resp.status_code, 200)
        next_data = next_resp.get_json()
        self.assertEqual(next_data["status"], "continue")

    def test_17_knowledge_check_results_and_history(self):
        """Verify saving attempt records score, awards defense points, and displays results."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        from database import save_knowledge_attempt, get_knowledge_attempt, get_db_connection
        sample_answers = [
            {
                "question_id": "m1_e_1",
                "question": "What does CPU stand for?",
                "options": ["Central Processing Unit", "Computer Personal Unit", "Control Power Utility", "Core Processing Utility"],
                "selected": 0,
                "correct": 0,
                "is_correct": True,
                "explanation": {"general": "CPU explanation", "why_correct": "Correct option", "why_incorrect": "Wrong options"}
            }
        ]
        attempt_id = save_knowledge_attempt(
            user_id=1,
            module_id=1,
            difficulty="Easy",
            score=18,
            total_questions=20,
            answers_list=sample_answers
        )
        self.assertIsNotNone(attempt_id)

        # Verify attempt retrieved
        att = get_knowledge_attempt(attempt_id, user_id=1)
        self.assertEqual(att["score"], 18)
        self.assertEqual(att["percentage"], 90.0)

        # Verify results page renders
        resp = self.client.get(f"/knowledge-check/1/Easy/results/{attempt_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"FINAL SCORE", resp.data)
        self.assertIn(b"18", resp.data)
        self.assertIn(b"90.0%", resp.data)
        self.assertIn(b"Cyber Mastery", resp.data)

    def test_18_dashboard_has_knowledge_check_card(self):
        """Verify the main dashboard has the Knowledge Check card and 6 total feature cards."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "cadet"

        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Knowledge Check", resp.data)
        self.assertIn(b"Simulation Drills", resp.data)
        self.assertIn(b"AI Threat Inspector", resp.data)
        self.assertIn(b"CTF Tactical Range", resp.data)
        self.assertIn(b"Incident War Room", resp.data)
        self.assertIn(b"Analytics &amp; Risk Profile", resp.data)
        self.assertIn(b"Knowledge Check", resp.data)
        self.assertNotIn(b"Defense Leaderboard", resp.data)

if __name__ == "__main__":
    unittest.main()