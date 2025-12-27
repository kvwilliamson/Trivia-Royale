#!/usr/bin/env python3
"""
Test script to verify Trivia Royale enhancements are working
"""

import os
import sys

def test_asset_paths():
    """Test that all assets exist in correct locations"""
    print("🔍 Testing asset paths...\n")
    
    assets_to_check = [
        # Audio files
        ("assets/audio/TriviaRoyaleTheme(2).mp3", "Intro Theme"),
        ("assets/audio/TQ_music_1.mp3", "Thinking Music 1"),
        ("assets/audio/TriviaChampion.mp3", "Winner Music"),
        ("assets/audio/FinalQuestionRound.mp3", "Final Round Music"),
        
        # Sound effects
        ("assets/audio/sfx/button_click.wav", "Button Click SFX"),
        ("assets/audio/sfx/correct_answer.wav", "Correct Answer SFX"),
        ("assets/audio/sfx/wrong_answer.wav", "Wrong Answer SFX"),
        ("assets/audio/sfx/round_transition.wav", "Round Transition SFX"),
        
        # Images
        ("assets/images/backgrounds/TriviaRoyaleScene(2).jpg", "Background Image"),
        ("assets/images/ui/checkmark.png", "Checkmark Icon"),
        ("assets/images/ui/x_mark.png", "X Mark Icon"),
        
        # Question files
        ("assets/questions_easy.json", "Easy Questions"),
        ("assets/questions_medium.json", "Medium Questions"),
        ("assets/questions_hard.json", "Hard Questions"),
    ]
    
    all_found = True
    for path, name in assets_to_check:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✓ {name:30s} - {path} ({size:,} bytes)")
        else:
            print(f"✗ {name:30s} - MISSING: {path}")
            all_found = False
    
    return all_found

def test_imports():
    """Test that all necessary modules can be imported"""
    print("\n\n🔍 Testing imports...\n")
    
    modules_to_test = [
        ('tkinter', 'Tkinter GUI'),
        ('pygame', 'Pygame Audio'),
        ('PIL', 'Pillow Image Processing'),
        ('pyttsx3', 'Text-to-Speech'),
        ('google.generativeai', 'Gemini AI'),
    ]
    
    all_imported = True
    for module, name in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {name:30s} - {module}")
        except ImportError as e:
            print(f"✗ {name:30s} - MISSING: {e}")
            all_imported = False
    
    return all_imported

def test_trivia_royale_classes():
    """Test that new classes exist in TriviaRoyale.py"""
    print("\n\n🔍 Testing TriviaRoyale classes...\n")
    
    try:
        sys.path.insert(0, os.getcwd())
        import TriviaRoyale
        
        classes_to_check = [
            ('SoundEffectManager', 'Sound Effect Manager'),
            ('FeedbackAnimator', 'Feedback Animator'),
            ('TriviaGame', 'Main Game Class'),
        ]
        
        all_found = True
        for class_name, description in classes_to_check:
            if hasattr(TriviaRoyale, class_name):
                print(f"✓ {description:30s} - {class_name}")
            else:
                print(f"✗ {description:30s} - MISSING: {class_name}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"✗ Failed to import TriviaRoyale: {e}")
        return False

def main():
    print("=" * 70)
    print("  Trivia Royale - Enhancement Verification Test")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Asset Paths", test_asset_paths()))
    results.append(("Module Imports", test_imports()))
    results.append(("TriviaRoyale Classes", test_trivia_royale_classes()))
    
    # Summary
    print("\n\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("\n🎉 All tests passed! Trivia Royale is ready to run!")
        print("\nYou can now start the game with:")
        print("  python TriviaRoyale.py")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        print("\nTry running:")
        print("  python generate_sound_effects.py")
        print("  python generate_ui_icons.py")
    print()

if __name__ == "__main__":
    main()
