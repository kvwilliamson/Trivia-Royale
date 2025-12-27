#!/usr/bin/env python3
"""
Auto-patcher for Trivia Royale Enhancements
This script applies all the necessary code changes to integrate sound effects and visual feedback
"""

import re

def patch_trivia_royale():
    """Apply all patches to TriviaRoyale.py"""
    
    with open('TriviaRoyale.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Patch 1: Initialize SFX and Feedback Animator (if not already there)
    if 'self.sfx = SoundEffectManager()' not in content:
        # Find the line after pygame mixer initialization
        pattern = r'(messagebox\.showerror\("Audio Error".*?\)\n\n)(        # Initialize game state variables)'
        replacement = r'\1        # --- Initialize Sound Effects and Visual Feedback ---\n        try:\n            self.sfx = SoundEffectManager()\n            print("\u2713 Sound effects loaded successfully")\n        except Exception as e:\n            print(f"### WARNING: Failed to initialize sound effects: {e}")\n            self.sfx = None\n        \n        try:\n            self.feedback_animator = FeedbackAnimator(self.root)\n            print("\u2713 Visual feedback system loaded")\n        except Exception as e:\n            print(f"### WARNING: Failed to initialize feedback animator: {e}")\n            self.feedback_animator = None\n\n\2'
        
        content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if n > 0:
            changes_made.append("✓ Added SFX and FeedbackAnimator initialization")
    
    # Patch 2: Add sound effects to handle_correctness_input
    if 'self.sfx.play' not in content or content.count('self.sfx.play') < 2:
        # Find handle_correctness_input method
        pattern = r'(if key_char == "y":\n)(        self\.scores\[self\.current_team\] \+= 10)'
        replacement = r'\1        # Play correct answer sound and show checkmark\n        if self.sfx:\n            self.sfx.play(\'correct\')\n        if self.feedback_animator:\n            self.feedback_animator.show_feedback(is_correct=True)\n        \2'
        
        content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes_made.append("✓ Added correct answer sound effect and visual feedback")
        
        # Add wrong answer feedback
        pattern = r'(elif key_char == "n":\n)(        pass  # No points)'
        replacement = r'\1        # Play wrong answer sound and show X\n        if self.sfx:\n            self.sfx.play(\'wrong\')\n        if self.feedback_animator:\n            self.feedback_animator.show_feedback(is_correct=False)\n        \2'
        
        content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes_made.append("✓ Added wrong answer sound effect and visual feedback")
    
    # Patch 3: Update music file paths to new structure
    music_updates = [
        (r'"TriviaRoyaleTheme\(2\)\.mp3"', '"audio/TriviaRoyaleTheme(2).mp3"'),
        (r'f"TQ_music_{random_number}\.mp3"', 'f"audio/TQ_music_{random_number}.mp3"'),
        (r'"TriviaChampion\.mp3"', '"audio/TriviaChampion.mp3"'),
        (r'"FinalQuestionRound\.mp3"', '"audio/FinalQuestionRound.mp3"'),
        (r'"TriviaRoyaleScene\(2\)\.jpg"', '"images/backgrounds/TriviaRoyaleScene(2).jpg"'),
    ]
    
    for old, new in music_updates:
        if old.replace('\\', '') in content and new not in content:
            content = re.sub(old, new, content)
            changes_made.append(f"✓ Updated asset path: {new}")
    
    # Patch 4: Add progress bar methodif 'def show_progress_bar(self):' not in content:
        # Find a good place to add it (after display_scoreboard)
        pattern = r'(def display_scoreboard\(self\):.*?return score_frame\n\n)'
        replacement = r'\1    def show_progress_bar(self):\n        """Display progress indicator showing current question/round"""\n        total_questions = self.num_rounds * self.num_teams\n        current_question = (self.current_round - 1) * self.num_teams + self.current_team + 1\n        \n        progress_text = f"Question {current_question} of {total_questions} | Round {self.current_round} of {self.num_rounds}"\n        progress_label = Label(\n            self.root,\n            text=progress_text,\n            font=FONTS["small"],\n            fg=COLORS["soft_coral"],\n            bg=COLORS["light_blue"]\n        )\n        progress_label.pack(side=tk.TOP, pady=5)\n        return progress_label\n\n'
        
        content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if n > 0:
            changes_made.append("✓ Added show_progress_bar() method")
    
    # Patch 5: Call progress bar in show_question
    if 'self.show_progress_bar()' not in content:
        pattern = r'(Label\(self\.root, text="Trivia Royale".*?\)\.pack\(pady=20\)\n)(        self\.display_scoreboard\(\))'
        replacement = r'\1        self.show_progress_bar()\n        \2'
        
        content, n = re.subn(pattern, replacement, content)
        if n > 0:
            changes_made.append("✓ Integrated progress bar into show_question()")
    
    # Save if changes were made
    if content != original_content:
        # Backup original
        with open('TriviaRoyale.py.backup', 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("📦 Created backup: TriviaRoyale.py.backup")
        
        # Write patched version
        with open('TriviaRoyale.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n🎉 Successfully patched TriviaRoyale.py!\n")
        print("Changes made:")
        for change in changes_made:
            print(f"  {change}")
        print(f"\nTotal patches applied: {len(changes_made)}")
        return True
    else:
        print("ℹ️  No changes needed - file appears to already be patched!")
        return False

if __name__ == "__main__":
    print("🔧 Trivia Royale Auto-Patcher\n")
    print("This script will automatically integrate:")
    print("  • Sound Effect Manager")
    print("  • Visual Feedback Animator")
    print("  • Progress Bar")
    print("  • Updated asset paths")
    print()
    
    try:
        success = patch_trivia_royale()
        if success:
            print("\n✅ Patching complete! You can now run: python TriviaRoyale.py")
            print("💡 Backup saved as: TriviaRoyale.py.backup")
        else:
            print("\n✅ File is already up to date!")
    except Exception as e:
        print(f"\n❌ Error during patching: {e}")
        print("Please apply changes manually using PROGRESS_REPORT.md")
