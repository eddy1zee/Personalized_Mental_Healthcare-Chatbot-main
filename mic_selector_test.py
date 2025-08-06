#!/usr/bin/env python3
"""
Microphone selector test - try different microphones
"""

import speech_recognition as sr
import pyaudio

def list_microphones():
    """List all available microphones"""
    print("🎤 Available Microphones:")
    print("=" * 30)
    
    p = pyaudio.PyAudio()
    mics = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            mics.append((i, info['name']))
            print(f"  {len(mics)}. Device {i}: {info['name']}")
    
    p.terminate()
    return mics

def test_specific_microphone(device_index):
    """Test a specific microphone"""
    print(f"\n🧪 Testing microphone device {device_index}...")
    
    r = sr.Recognizer()
    
    try:
        with sr.Microphone(device_index=device_index) as source:
            print("🔧 Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            # Very sensitive settings
            r.energy_threshold = 50
            
            print(f"📊 Energy threshold: {r.energy_threshold}")
            print("🎤 SPEAK NOW! (10 seconds)")
            
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            print("✅ Audio captured!")
            
            text = r.recognize_google(audio)
            print(f"🎉 SUCCESS: '{text}'")
            return True
            
    except sr.WaitTimeoutError:
        print("⏰ No speech detected")
        return False
    except sr.UnknownValueError:
        print("⚠️  Audio captured but couldn't understand")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎤 Microphone Selector Test")
    print("=" * 40)
    
    # List all microphones
    mics = list_microphones()
    
    if not mics:
        print("❌ No microphones found!")
        return
    
    print(f"\n📊 Found {len(mics)} microphone(s)")
    
    # Test each microphone
    for i, (device_index, name) in enumerate(mics):
        print(f"\n{'='*50}")
        print(f"Testing #{i+1}: {name}")
        print('='*50)
        
        success = test_specific_microphone(device_index)
        
        if success:
            print(f"🎉 MICROPHONE #{i+1} WORKS!")
            print(f"Device Index: {device_index}")
            print(f"Name: {name}")
            break
        else:
            print(f"❌ Microphone #{i+1} failed")
    
    print("\n💡 If none work, try:")
    print("  • Check Windows microphone permissions")
    print("  • Increase microphone volume in Windows")
    print("  • Speak louder and closer to microphone")
    print("  • Test microphone in Windows Voice Recorder first")

if __name__ == "__main__":
    main()
