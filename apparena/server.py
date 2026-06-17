#!/usr/bin/env python3
"""
AppArena Server - The Living Brain Interface
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, os, sys, urllib.parse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))
from brain import AppArenaBrain

brain = AppArenaBrain()

class ArenaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/chat.html'
        elif self.path == '/api/brain/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            alive_status = brain.get_alive_status()
            thinking = brain.think_about_user()
            alive_status["thinking"] = thinking
            
            self.wfile.write(json.dumps(alive_status).encode())
            return
        elif self.path == '/api/brain/suggest':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            suggestion = brain.suggest_next_challenge()
            self.wfile.write(json.dumps(suggestion).encode())
            return
        elif self.path.startswith('/api/observe/'):
            event_type = self.path.split('/')[-1]
            brain.observe(event_type, {"source": "web"})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = brain._get_response(event_type, {})
            self.wfile.write(json.dumps(response).encode())
            return
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            message = data.get('message', '')
            
            # Process message through brain
            brain.observe("chat", {"message": message, "source": "web"})
            response = brain._get_response("chat", {"message": message})
            
            # Get brain status for context
            status = brain.get_alive_status()
            thinking = brain.think_about_user()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                "type": "chat_response",
                "response": response.get("message", "I'm thinking..."),
                "emotion": response.get("emotion", "present"),
                "tip": response.get("tip", ""),
                "personality": status.get("personality", {}),
                "thinking": thinking,
                "alive": status.get("alive", True)
            }).encode())
            return
        
        self.send_response(404)
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def main():
    port = 8081
    server = HTTPServer(('0.0.0.0', port), ArenaHandler)
    print(f"AppArena Brain running at http://localhost:{port}")
    print(f"Brain status: {brain.get_alive_status()['alive']}")
    print("The app is alive and learning!")
    server.serve_forever()

if __name__ == "__main__":
    main()
