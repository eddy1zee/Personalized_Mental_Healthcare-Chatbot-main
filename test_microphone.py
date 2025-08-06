#!/usr/bin/env python3
"""
Test microphone access and audio recording
"""

import speech_recognition as sr
import pyaudio
import time

def test_microphone_access():
    """Test basic microphone access"""
    print("🎤 Testing Microphone Access...")
    print("=" * 40)
    
    try:
        # Test PyAudio
        p = pyaudio.PyAudio()
        print(f"✅ PyAudio initialized successfully")
        print(f"📊 Available audio devices: {p.get_device_count()}")
        
        # List audio devices
        print("\n🔍 Audio Devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Input devices only
                print(f"  Device {i}: {info['name']} (Inputs: {info['maxInputChannels']})")
        
        p.terminate()
        
        # Test Speech Recognition
        print("\n🎤 Testing Speech Recognition...")
        r = sr.Recognizer()
        
        # Test microphone access
        with sr.Microphone() as source:
            print("✅ Microphone accessed successfully")
            print("🔧 Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print(f"📊 Energy threshold: {r.energy_threshold}")
            
            print("\n🎤 SPEAK NOW! (5 seconds)")
            print("Say something like: 'Hello, this is a test'")
            
            try:
                # Listen for audio
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                print("✅ Audio captured successfully!")
                print(f"📊 Audio data length: {len(audio.frame_data)} bytes")
                
                # Try to recognize
                print("🔄 Attempting recognition with Google...")
                try:
                    text = r.recognize_google(audio)
                    print(f"✅ SUCCESS! Recognized: '{text}'")
                    return True
                except sr.UnknownValueError:
                    print("⚠️  Audio captured but could not understand speech")
                    print("💡 Try speaking louder or more clearly")
                    return False
                except sr.RequestError as e:
                    print(f"❌ Google Speech Recognition error: {e}")
                    return False
                    
            except sr.WaitTimeoutError:
                print("⏰ No speech detected within timeout")
                print("💡 Possible issues:")
                print("  • Microphone not working")
                print("  • Volume too low")
                print("  • Wrong microphone selected")
                print("  • Microphone permissions denied")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_microphone_permissions():
    """Test microphone permissions"""
    print("\n🔒 Testing Microphone Permissions...")
    print("=" * 40)
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Try to open a stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        print("✅ Microphone stream opened successfully")
        
        # Read a small amount of data
        data = stream.read(1024)
        print(f"✅ Audio data read successfully: {len(data)} bytes")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone permission error: {e}")
        print("\n💡 Solutions:")
        print("  • Check Windows microphone permissions")
        print("  • Ensure microphone is not used by another app")
        print("  • Try running as administrator")
        print("  • Check microphone hardware connection")
        return False

def main():
    """Main test function"""
    print("🧪 Microphone & Speech Recognition Test")
    print("=" * 50)
    
    # Test permissions first
    permissions_ok = test_microphone_permissions()
    
    if permissions_ok:
        # Test full speech recognition
        speech_ok = test_microphone_access()
        
        print("\n📋 TEST RESULTS")
        print("=" * 20)
        print(f"🔒 Microphone Access: {'✅ OK' if permissions_ok else '❌ Failed'}")
        print(f"🎤 Speech Recognition: {'✅ OK' if speech_ok else '❌ Failed'}")
        
        if permissions_ok and speech_ok:
            print("\n🎉 SUCCESS! Your microphone is working perfectly!")
            print("The Streamlit app should work with voice input.")
        elif permissions_ok:
            print("\n⚠️  Microphone works but speech recognition failed")
            print("💡 Try speaking louder or check internet connection")
        else:
            print("\n❌ Microphone access failed")
            print("💡 Check permissions and hardware")
    
    print("\n🚀 Next steps:")
    print("If this test passes, try the Streamlit app voice feature again")

if __name__ == "__main__":
    main()
