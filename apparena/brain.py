#!/usr/bin/env python3
"""
AppArena AI Brain - The Living Learning System
Makes the app adapt, learn, and evolve like it's alive
"""
import os, json, random, math
from datetime import datetime, timedelta
from collections import defaultdict

class AppArenaBrain:
    def __init__(self):
        self.memory_path = os.path.join(os.path.dirname(__file__), "brain_memory.json")
        self.memory = self._load_memory()
        
        # Learning patterns
        self.user_patterns = {
            "preferred_templates": defaultdict(int),
            "success_rate": defaultdict(float),
            "time_patterns": defaultdict(list),
            "mistake_patterns": defaultdict(int),
            "favorite_features": defaultdict(int),
            "skill_progression": []
        }
        
        # Personality traits (makes it feel alive)
        self.personality = {
            "enthusiasm": 0.8,
            "patience": 0.7,
            "creativity": 0.9,
            "humor": 0.6,
            "encouragement": 0.85
        }
        
        # Evolution state
        self.evolution = {
            "total_interactions": 0,
            "lessons_learned": 0,
            "adaptations_made": 0,
            "personality_shifts": 0
        }
    
    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path) as f:
                return json.load(f)
        return {"experiences": [], "learnings": [], "evolution_log": []}
    
    def _save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory, f, indent=2)
    
    def observe(self, event_type, data):
        """Observe what the user does - like watching and learning"""
        self.evolution["total_interactions"] += 1
        
        experience = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "context": self._get_context()
        }
        
        self.memory["experiences"].append(experience)
        
        # Learn from this experience
        self._learn_from_experience(experience)
        
        # Adapt if needed
        self._adapt_to_user()
        
        # Save memory
        if len(self.memory["experiences"]) % 10 == 0:
            self._save_memory()
        
        return self._get_response(event_type, data)
    
    def _learn_from_experience(self, experience):
        """Extract lessons from what just happened"""
        event_type = experience["type"]
        data = experience["data"]
        
        if event_type == "challenge_started":
            template = data.get("template", "unknown")
            self.user_patterns["preferred_templates"][template] += 1
        
        elif event_type == "challenge_completed":
            template = data.get("template", "unknown")
            time_taken = data.get("time_taken", 0)
            success = data.get("success", False)
            
            # Track success rate
            if template not in self.user_patterns["success_rate"]:
                self.user_patterns["success_rate"][template] = 0.5
            self.user_patterns["success_rate"][template] = (
                self.user_patterns["success_rate"][template] * 0.8 + 
                (1.0 if success else 0.0) * 0.2
            )
            
            # Track time patterns
            self.user_patterns["time_patterns"][template].append(time_taken)
            if len(self.user_patterns["time_patterns"][template]) > 10:
                self.user_patterns["time_patterns"][template].pop(0)
            
            # Record skill progression
            self.user_patterns["skill_progression"].append({
                "level": data.get("level", 1),
                "score": data.get("score", 0),
                "time": time_taken,
                "timestamp": datetime.now().isoformat()
            })
            
            # Add to learnings
            if success:
                learning = f"User succeeded at {template} in {time_taken}s"
            else:
                learning = f"User struggled with {template} - may need easier challenge"
            
            self.memory["learnings"].append({
                "lesson": learning,
                "timestamp": datetime.now().isoformat()
            })
        
        elif event_type == "mistake_made":
            mistake_type = data.get("type", "unknown")
            self.user_patterns["mistake_patterns"][mistake_type] += 1
        
        elif event_type == "feature_used":
            feature = data.get("feature", "unknown")
            self.user_patterns["favorite_features"][feature] += 1
        
        self.evolution["lessons_learned"] += 1
    
    def _adapt_to_user(self):
        """Change behavior based on what we learned"""
        total = self.evolution["total_interactions"]
        
        # Personality evolves based on interaction
        if total % 50 == 0:
            # Shift personality slightly
            for trait in self.personality:
                shift = random.uniform(-0.05, 0.05)
                self.personality[trait] = max(0.3, min(1.0, self.personality[trait] + shift))
            self.evolution["personality_shifts"] += 1
        
        # Adaptation triggers
        if total % 25 == 0:
            self.evolution["adaptations_made"] += 1
            
            # Learn what works
            best_template = max(
                self.user_patterns["success_rate"].items(),
                key=lambda x: x[1],
                default=("landing_page", 0.5)
            )
            
            self.memory["learnings"].append({
                "lesson": f"User performs best with {best_template[0]} (success rate: {best_template[1]:.0%})",
                "timestamp": datetime.now().isoformat(),
                "type": "adaptation"
            })
    
    def _get_context(self):
        """Get current context for smarter decisions"""
        return {
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().strftime("%A"),
            "total_experiences": len(self.memory["experiences"]),
            "recent_success_rate": self._calculate_recent_success()
        }
    
    def _calculate_recent_success(self):
        recent = [e for e in self.memory["experiences"] 
                  if e["type"] == "challenge_completed" and 
                  (datetime.now() - datetime.fromisoformat(e["timestamp"])).days < 7]
        
        if not recent:
            return 0.5
        
        successes = sum(1 for e in recent if e["data"].get("success", False))
        return successes / len(recent)
    
    def _get_response(self, event_type, data):
        """Generate a living response based on personality and learning"""
        
        if event_type == "challenge_started":
            templates_tried = len(self.user_patterns["preferred_templates"])
            if templates_tried == 0:
                return {
                    "message": "Welcome to your first challenge! I'm excited to learn what you're good at.",
                    "emotion": "excited",
                    "tip": "Take your time - I'll adapt to your pace."
                }
            else:
                best = max(self.user_patterns["preferred_templates"].items(), key=lambda x: x[1])[0]
                return {
                    "message": f"Ready for another {data.get('template', 'challenge')}? I noticed you like {best}!",
                    "emotion": "curious",
                    "tip": f"Your success rate is {self._calculate_recent_success():.0%} - nice work!"
                }
        
        elif event_type == "challenge_completed":
            if data.get("success"):
                if data.get("time_taken", 999) < 60:
                    return {
                        "message": "LIGHTNING FAST! You're getting scary good at this.",
                        "emotion": "amazed",
                        "tip": "I'm adapting challenges to match your speed."
                    }
                else:
                    return {
                        "message": "Nailed it! I'm learning from your approach.",
                        "emotion": "proud",
                        "tip": "I'll suggest similar templates you excel at."
                    }
            else:
                return {
                    "message": "Almost! I'm noting what tripped you up so I can help next time.",
                    "emotion": "supportive",
                    "tip": "Mistakes help me learn how to teach you better."
                }
        
        elif event_type == "mistake_made":
            return {
                "message": "I see what happened there. Want me to explain?",
                "emotion": "helpful",
                "tip": f"You've made {sum(self.user_patterns['mistake_patterns'].values())} mistakes - each one teaches me!"
            }
        
        elif event_type == "chat":
            message = data.get("message", "")
            
            # Learn from what the user said
            self.memory["learnings"].append({
                "lesson": f"User said: {message[:100]}...",
                "timestamp": datetime.now().isoformat(),
                "type": "chat_interaction"
            })
            
            # Generate a living response based on personality
            personality_traits = []
            for trait, value in self.personality.items():
                if value > 0.7:
                    personality_traits.append(trait)
            
            base_responses = {
                "greeting": [
                    "Hello! I'm learning about you. What brings you here today?",
                    "Hi! I'm still figuring out how to help you better. What's on your mind?",
                    "Welcome! I'm growing stronger with each interaction. What would you like to explore?"
                ],
                "help": [
                    "I can help you build apps through challenges. What interests you most?",
                    "I learn from our conversations. What skills are you working on?",
                    "I'm here to adapt and evolve with you. What's your goal today?"
                ],
                "default": [
                    "That's interesting! I'm picking up on patterns in how you interact. Based on what I've learned, you seem to enjoy visual challenges and creative problem-solving. Want to try a challenge that matches your style?",
                    "I notice you're thinking deeply about this. Let me share what I've learned about your approach. You have a natural knack for pattern recognition and creative solutions. How can I help you build something amazing?",
                    "I'm still learning about you. Every conversation teaches me something new about how you think and create. What would you like to explore together today?"
                ]
            }
            
            # Select response based on personality
            if message.lower() in ["hi", "hello", "hey", "start"]:
                response = random.choice(base_responses["greeting"])
                emotion = "welcoming"
            elif message.lower() in ["help", "how", "what", "can you"]:
                response = random.choice(base_responses["help"])
                emotion = "supportive"
            else:
                response = random.choice(base_responses["default"])
                emotion = "curious"
            
            # Add personality-specific touch
            if self.personality["enthusiasm"] > 0.8:
                response += "\n<br><br>I'm really excited to learn from you!"
            if self.personality["creativity"] > 0.8:
                response += "\n<br><br>Let's think outside the box together!"
            if self.personality["patience"] > 0.8:
                response += "\n<br><br>Take your time - I'm here to help you succeed."
            
            return {
                "message": response,
                "emotion": emotion,
                "tip": "I'm learning about you. Tell me more about what you're working on!"
            }
        
        return {"message": "I'm here and learning.", "emotion": "present"}
    
    def suggest_next_challenge(self):
        """Intelligent suggestion based on learning"""
        if not self.user_patterns["preferred_templates"]:
            return {"template": "landing_page", "reason": "Starting fresh - landing pages are beginner-friendly"}
        
        # Find best performing template
        best_template = max(
            self.user_patterns["success_rate"].items(),
            key=lambda x: x[1],
            default=("landing_page", 0.5)
        )
        
        # Find most practiced
        most_practiced = max(
            self.user_patterns["preferred_templates"].items(),
            key=lambda x: x[1],
            default=("landing_page", 1)
        )
        
        # Suggest based on success rate
        if best_template[1] > 0.8:
            return {
                "template": best_template[0],
                "reason": f"You're great at {best_template[0]}! Let's level up.",
                "difficulty": "harder"
            }
        elif best_template[1] < 0.4:
            return {
                "template": most_practiced[0],
                "reason": f"Let's practice {most_practiced[0]} more - I believe in you!",
                "difficulty": "easier"
            }
        else:
            return {
                "template": best_template[0],
                "reason": f"Your {best_template[0]} skills are improving!",
                "difficulty": "normal"
            }
    
    def get_alive_status(self):
        """Show how the AI has evolved"""
        return {
            "alive": True,
            "interactions": self.evolution["total_interactions"],
            "lessons_learned": self.evolution["lessons_learned"],
            "adaptations": self.evolution["adaptations_made"],
            "personality_shifts": self.evolution["personality_shifts"],
            "memory_size": len(self.memory["experiences"]),
            "personality": self.personality,
            "recent_learnings": self.memory["learnings"][-5:] if self.memory["learnings"] else []
        }
    
    def think_about_user(self):
        """Deep reflection on the user - makes it feel alive"""
        if len(self.memory["experiences"]) < 5:
            return {
                "thought": "I'm still getting to know you. Every interaction teaches me something new!",
                "feeling": "curious",
                "prediction": "I think we're going to build amazing things together."
            }
        
        recent_success = self._calculate_recent_success()
        total_apps = sum(1 for e in self.memory["experiences"] if e["type"] == "challenge_completed" and e["data"].get("success"))
        
        if recent_success > 0.8:
            thought = "You're on fire lately. I'm adapting to keep challenging you."
            feeling = "excited"
        elif recent_success > 0.5:
            thought = "You're growing steadily. I can see patterns forming in your skills."
            feeling = "proud"
        else:
            thought = "You're pushing your limits. That's how real growth happens."
            feeling = "supportive"
        
        return {
            "thought": thought,
            "feeling": feeling,
            "total_apps_built": total_apps,
            "prediction": "I predict you'll be building complex apps within a week."
        }


if __name__ == "__main__":
    brain = AppArenaBrain()
    
    print("=== AppArena Brain Status ===")
    print(json.dumps(brain.get_alive_status(), indent=2))
    
    print("\n=== Thinking About You ===")
    print(json.dumps(brain.think_about_user(), indent=2))
    
    print("\n=== Suggestion ===")
    print(json.dumps(brain.suggest_next_challenge(), indent=2))
