#!/usr/bin/env python3
"""
Quick microphone test - more sensitive settings
"""

import speech_recognition as sr
import time

def quick_test():
    print("🎤 Quick Microphone Test")
    print("=" * 30)
    
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🔧 Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        # Make it more sensitive
        original_threshold = r.energy_threshold
        r.energy_threshold = max(50, r.energy_threshold * 0.3)  # Much more sensitive
        
        print(f"📊 Original threshold: {original_threshold:.1f}")
        print(f"📊 New threshold: {r.energy_threshold:.1f}")
        print()
        print("🎤 SPEAK NOW! Say 'Hello test' LOUDLY!")
        print("⏰ You have 20 seconds...")
        
        try:
            # Very generous timeout and phrase limit
            audio = r.listen(source, timeout=20, phrase_time_limit=30)
            print("✅ Audio captured!")
            
            print("🔄 Recognizing with Google...")
            text = r.recognize_google(audio)
            print(f"🎉 SUCCESS: '{text}'")
            
        except sr.WaitTimeoutError:
            print("❌ Still no speech detected")
            print("💡 Your microphone might be:")
            print("  • Too quiet/muted")
            print("  • Wrong device selected")
            print("  • Hardware issue")
            
        except sr.UnknownValueError:
            print("⚠️  Audio captured but couldn't understand")
            print("💡 Try speaking more clearly")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
