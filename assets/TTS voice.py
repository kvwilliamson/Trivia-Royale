# --- Script to Sample SPECIFIC English TTS Voices on macOS ---
import pyttsx3
import time

def sample_specific_voices(target_voice_names):
    """
    Initializes pyttsx3, finds specific voices by name,
    and speaks sample text with each found voice.
    Designed with macOS voices in mind.
    """

    print("Initializing Text-to-Speech engine (attempting macOS driver)...")
    try:
        # Explicitly trying the macOS driver, though default often works.
        engine = pyttsx3.init(driverName='nsss')
    except Exception as e_nsss:
        print(f"  > INFO: Failed to init with 'nsss' driver ({e_nsss}), trying default.")
        try:
            engine = pyttsx3.init()
        except Exception as e_default:
            print(f"\n--- ERROR ---")
            print(f"Failed to initialize pyttsx3 engine with any driver: {e_default}")
            print("Ensure macOS text-to-speech services are functional.")
            return

    try:
        print("Getting available voices...")
        all_voices = engine.getProperty('voices')
        if not all_voices:
            print("No voices found by the engine.")
            engine.stop()
            return

        # Normalize target names to lowercase for comparison
        target_names_lower = [name.lower() for name in target_voice_names]
        print(f"Filtering for voices containing: {', '.join(target_voice_names)}...")

        selected_voices = []
        for voice in all_voices:
            # Ensure the voice has a name attribute
            if hasattr(voice, 'name') and voice.name:
                voice_name_lower = voice.name.lower()
                # Check if any of the target names are substrings of the voice name
                if any(target in voice_name_lower for target in target_names_lower):
                    # Add only if it's not already added (handles potential duplicates if names overlap)
                    if voice not in selected_voices:
                        selected_voices.append(voice)

        if not selected_voices:
            print("\n--- WARNING ---")
            print(f"Could not find any voices matching the names: {', '.join(target_voice_names)}.")
            print("Please double-check the names and available voices in System Settings > Accessibility > Spoken Content > System Voice.")
            engine.stop()
            return

        print(f"\nFound {len(selected_voices)} matching voice(s).")

        default_text = "This is a test using one of the selected voices."
        sample_text = input(f"Enter the text you want to hear (or press Enter for default):\n> ")
        if not sample_text.strip():
            sample_text = default_text

        print("\n--- Starting Voice Sampling ---")
        print(f"Speaking: \"{sample_text}\"")

        # Sort selected voices by name for consistent order (optional)
        selected_voices.sort(key=lambda v: v.name)

        for i, voice in enumerate(selected_voices):
            print(f"\n--- Voice {i+1}/{len(selected_voices)} ---")
            print(f"  ID: {voice.id}")
            print(f"  Name: {voice.name}")
            if hasattr(voice, 'languages'): print(f"  Languages: {voice.languages}")
            if hasattr(voice, 'gender'): print(f"  Gender: {voice.gender}")
            # Age attribute might not be present on macOS voices
            # if hasattr(voice, 'age'): print(f"  Age: {voice.age}")

            try:
                engine.setProperty('voice', voice.id)
                # Optional: Adjust rate or volume
                # engine.setProperty('rate', 160) # Slightly faster perhaps?
                # engine.setProperty('volume', 0.9)

                print("  Speaking...")
                engine.say(sample_text)
                engine.runAndWait()
                print("  ...Done.")
                time.sleep(0.5) # Pause between voices

            except Exception as speak_error:
                print(f"  ERROR: Could not use voice ID '{voice.id}': {speak_error}")

        print("\n--- Voice Sampling Complete ---")
        print("Confirm which voice (and its ID) you prefer for the main game.")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    finally:
        # Ensure the engine is stopped
        if 'engine' in locals() and engine._inLoop:
             try: engine.endLoop()
             except: pass
        elif 'engine' in locals():
             try: pass # del engine optional
             except: pass


# --- Main execution ---
if __name__ == "__main__":
    # Define the list of voice names you liked
    voices_to_sample = ["Daniel", "Moira", "Rishi", "Samantha", "Tessa"]
    sample_specific_voices(voices_to_sample)