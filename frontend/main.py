#!/usr/bin/env python3
"""
IATRO Frontend - Modern Python GUI for Pediatric Diagnostic System
Completely redesigned with coherent design system inspired by Palantir
"""

import sys
import os
import argparse
from pathlib import Path
from collections import defaultdict

# Add parent directory to path to import inference module
# Handle PyInstaller executable case
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # sys._MEIPASS is the temporary directory where PyInstaller extracts files
    base_path = sys._MEIPASS
    # Try to add parent directory if we can determine it
    if hasattr(sys, 'executable'):
        exe_dir = os.path.dirname(sys.executable)
        parent_dir = os.path.dirname(exe_dir) if os.path.basename(exe_dir).endswith('.app') else exe_dir
        if os.path.exists(parent_dir):
            sys.path.insert(0, parent_dir)
    sys.path.insert(0, base_path)
else:
    # Running as script
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import customtkinter as ctk
    from PIL import Image, ImageTk
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import design system
try:
    from design_system import (
        COLORS, Colors, Typography, Spacing, Radius,
        TopBar, SymptomCard, DiagnosisCard, CompletionSummary,
        ConfidenceIndicator, PanelHeader
    )
except ImportError as e:
    print(f"ERROR: Could not import design system: {e}")
    sys.exit(1)

# Import inference logic
try:
    from inference import (
        load_data,
        select_next_symptoms,
        update_posteriors_positive,
        calculate_confidence,
        explain_symptom,
        categorize_symptom,
        compute_scarcity_boosts,
        dynamic_required_hits,
        CLUSTERS,
        SUCCESS_CONFIDENCE,
        MIN_EVIDENCE_ANSWERS,
        EARLY_FINALIZE_TOPP,
    )
except ImportError as e:
    print(f"ERROR: Could not import inference module: {e}")
    sys.exit(1)

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DiagnosticApp(ctk.CTk):
    """Main application window with Palantir-inspired design system"""
    
    def __init__(self, db_path="pediatric.db"):
        super().__init__()
        
        self.db_path = db_path
        self.diseases = {}
        self.priors = {}
        self.symptom_map = {}
        
        # Diagnostic state
        self.candidates = {}
        self.asked = set()
        self.symptom_path = []  # Track order of symptoms selected
        self.answered_with_lr = 0
        self.evidence_hits_by_disease = defaultdict(int)
        self.cluster_strength = {c: 0.0 for c in CLUSTERS}
        self.scarcity_boosts = {}
        self.consecutive_low_gain = 0
        
        # UI state
        self.current_symptoms = []
        self.diagnosis_finalized = False
        self.selected_symptom = None
        
        self.setup_window()
        self.load_data()
        self.create_ui()
        self.start_new_diagnosis()
    
    def setup_window(self):
        """Configure main window"""
        self.title("IATRO - Pediatric Diagnostic System")
        self.geometry("1600x950")
        self.configure(fg_color=Colors.BG_PRIMARY)
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_data(self):
        """Load disease data from database"""
        try:
            # Handle PyInstaller executable case
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - let load_data() handle path resolution
                # It will check sys._MEIPASS and other locations
                self.diseases, self.priors, self.symptom_map = load_data(self.db_path)
            else:
                # Running as script - try relative paths
                db_relative = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.db_path)
                if os.path.exists(db_relative):
                    self.diseases, self.priors, self.symptom_map = load_data(db_relative)
                elif os.path.exists(self.db_path):
                    self.diseases, self.priors, self.symptom_map = load_data(self.db_path)
                else:
                    # Fallback: let load_data() try to find it
                    self.diseases, self.priors, self.symptom_map = load_data(self.db_path)
            
            self.scarcity_boosts = compute_scarcity_boosts(self.symptom_map, list(self.diseases.keys()))
        except Exception as e:
            self.show_error(f"Failed to load database: {e}")
            sys.exit(1)
    
    def create_ui(self):
        """Create the main UI layout"""
        # Main container with padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top bar with title and new diagnosis button
        self.top_bar = TopBar(
            main_container,
            title="IATRO",
            subtitle="Pediatric Diagnostic Inference System",
            on_new_diagnosis=self.start_new_diagnosis
        )
        self.top_bar.pack(fill="x", pady=(0, 20))
        
        # Main content area - two columns
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Left column - Symptom selection (60% width)
        left_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_medium"], corner_radius=8)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right column - Diagnosis results (40% width)
        right_panel = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_medium"], corner_radius=8)
        right_panel.pack(side="right", fill="both", expand=False, padx=(10, 0), ipadx=20)
        right_panel.configure(width=500)
        
        # Store references
        self.left_panel = left_panel
        self.right_panel = right_panel
        
        self.create_symptom_panel(left_panel)
        self.create_diagnosis_panel(right_panel)
    
    def create_symptom_panel(self, parent):
        """Create symptom selection panel"""
        # Header using PanelHeader component
        self.symptom_header = PanelHeader(
            parent,
            title="Search or Select a Symptom",
            action_text="Skip",
            action_command=self.skip_all_symptoms
        )
        
        # Search frame - shown until diagnosis is finalized
        self.search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Pack initially so placeholder shows on launch
        self.search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search for a symptom",
            font=ctk.CTkFont(size=13),
            height=36,
            fg_color=COLORS["bg_light"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"]  # Muted white/gray for placeholder
        )
        self.search_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        self.search_entry.bind("<Return>", self.on_search_enter)
        
        self.search_results_frame = None
        self.search_results_scroll = None
        
        # Container for symptom list and search results
        self.symptom_content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.symptom_content_frame.pack(fill="both", expand=True)
        
        # Scrollable symptom list
        scroll_frame = ctk.CTkScrollableFrame(
            self.symptom_content_frame,
            fg_color=COLORS["bg_light"],
            corner_radius=6
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.symptom_scroll_frame = scroll_frame
        self.symptom_buttons = []
        self.selected_symptom = None  # Track currently selected symptom
        self.search_query = ""  # Track current search query
    
    def create_diagnosis_panel(self, parent):
        """Create diagnosis results panel"""
        # Header
        header = ctk.CTkLabel(
            parent,
            text="Diagnosis Results",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_primary"]
        )
        header.pack(pady=(20, 10))
        
        # Confidence indicator using ConfidenceIndicator component
        self.confidence_indicator = ConfidenceIndicator(parent)
        self.confidence_indicator.pack(fill="x", padx=20, pady=(0, 20))
        
        # Top diagnoses list
        diagnoses_label = ctk.CTkLabel(
            parent,
            text="Top Diagnoses",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        diagnoses_label.pack(pady=(10, 10))
        
        # Scrollable diagnoses
        diagnoses_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color=COLORS["bg_light"],
            corner_radius=8
        )
        diagnoses_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.diagnoses_scroll_frame = diagnoses_scroll
        self.diagnosis_cards = []
    
    def start_new_diagnosis(self):
        """Reset state and start a new diagnosis"""
        self.candidates = dict(self.priors)
        self.asked = set()
        self.symptom_path = []
        self.answered_with_lr = 0
        self.evidence_hits_by_disease = defaultdict(int)
        self.cluster_strength = {c: 0.0 for c in CLUSTERS}
        self.consecutive_low_gain = 0
        self.diagnosis_finalized = False
        self.search_query = ""
        
        # Clear search entry
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, "end")
        
        self.update_ui()
    
    def update_ui(self):
        """Update the entire UI with current state"""
        self.update_symptom_panel()
        self.update_diagnosis_panel()
        self.check_convergence()
    
    def update_symptom_panel(self):
        """Update symptom selection panel"""
        # Show search bar until diagnosis is finalized
        if not self.diagnosis_finalized:
            # Pack search frame before symptom_content_frame to maintain order
            try:
                self.search_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.symptom_content_frame)
            except:
                # Fallback if before doesn't work (shouldn't happen)
                self.search_frame.pack(fill="x", padx=20, pady=(0, 10))
            # Show search results if there's a query
            if self.search_query:
                self.show_search_results()
                return
        else:
            self.search_frame.pack_forget()
            # Hide search results if visible
            if self.search_results_frame:
                self.search_results_frame.pack_forget()
        
        # Make sure symptom scroll frame is visible (in case it was hidden by search)
        self.symptom_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Clear existing buttons
        for widget in self.symptom_scroll_frame.winfo_children():
            widget.destroy()
        self.symptom_buttons = []
        
        # Show skip button if diagnosis is not finalized
        if not self.diagnosis_finalized and self.symptom_header.action_btn:
            self.symptom_header.action_btn.pack(side="right", padx=(10, 0))
        
        if self.diagnosis_finalized:
            self.show_completion_summary()
            return
        
        # Get next symptoms
        next_symptoms = select_next_symptoms(
            self.candidates,
            self.symptom_map,
            self.asked,
            top_n=10,
            cluster_strength=self.cluster_strength,
            scarcity_boosts=self.scarcity_boosts
        )
        
        self.current_symptoms = next_symptoms
        
        if not next_symptoms:
            no_symptoms_label = ctk.CTkLabel(
                self.symptom_scroll_frame,
                text="No further symptoms available",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"]
            )
            no_symptoms_label.pack(pady=50)
            return
        
        # Create symptom buttons
        for i, symptom in enumerate(next_symptoms):
            self.create_symptom_button(symptom, i)
    
    def on_search_change(self, event=None):
        """Handle search input changes"""
        query = self.search_entry.get().strip().lower()
        self.search_query = query
        
        if query:
            self.show_search_results()
        else:
            # Clear search results and show normal symptom list
            if self.search_results_frame:
                self.search_results_frame.pack_forget()
            # Make sure normal symptom scroll frame is visible
            self.symptom_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            # Don't call update_symptom_panel here to avoid recursion - just continue with normal flow
    
    def on_search_enter(self, event=None):
        """Handle Enter key in search - select first result if available"""
        query = self.search_entry.get().strip().lower()
        if not query:
            return
        
        # Get filtered symptoms (excluding already asked ones)
        all_symptoms = list(self.symptom_map.keys())
        filtered = [s for s in all_symptoms if query in s.lower() and s not in self.asked]
        
        if filtered:
            # Select the first matching symptom
            self.select_symptom(filtered[0])
            self.search_entry.delete(0, "end")
            self.search_query = ""
    
    def show_search_results(self):
        """Show filtered search results"""
        query = self.search_entry.get().strip().lower()
        if not query:
            return
        
        # Get all available symptoms
        all_symptoms = list(self.symptom_map.keys())
        
        # Filter symptoms that match the query and haven't been asked yet
        filtered = [s for s in all_symptoms if query in s.lower() and s not in self.asked]
        
        # Sort by relevance (exact matches first, then by position)
        filtered.sort(key=lambda s: (not s.lower().startswith(query), s.lower().find(query), s.lower()))
        
        # Limit to top 20 results
        filtered = filtered[:20]
        
        # Hide normal symptom scroll frame
        self.symptom_scroll_frame.pack_forget()
        
        # Create or update search results frame
        if self.search_results_frame:
            # Clear existing widgets
            for widget in self.search_results_scroll.winfo_children():
                widget.destroy()
        else:
            self.search_results_frame = ctk.CTkFrame(
                self.symptom_content_frame,
                fg_color=COLORS["bg_light"],
                corner_radius=6
            )
            self.search_results_scroll = ctk.CTkScrollableFrame(
                self.search_results_frame,
                fg_color=COLORS["bg_light"],
                corner_radius=6
            )
            self.search_results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show search results frame
        self.search_results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if not filtered:
            no_results_label = ctk.CTkLabel(
                self.search_results_scroll,
                text=f"No symptoms found matching '{query}'",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"]
            )
            no_results_label.pack(pady=50)
            return
        
        # Show result count
        count_label = ctk.CTkLabel(
            self.search_results_scroll,
            text=f"Found {len(filtered)} symptom{'s' if len(filtered) != 1 else ''}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        count_label.pack(pady=(0, 10))
        
        # Create buttons for filtered symptoms
        for symptom in filtered:
            self.create_search_result_button(symptom)
    
    def create_search_result_button(self, symptom):
        """Create a clickable symptom button for search results"""
        is_selected = (self.selected_symptom == symptom)
        explanation = explain_symptom(symptom)
        
        symptom_card = SymptomCard(
            self.search_results_scroll,
            symptom=symptom,
            explanation=explanation,
            is_selected=is_selected,
            on_click=lambda s=symptom: self.on_symptom_click(s),
            on_confirm=lambda s=symptom: self.confirm_symptom(s)
        )
        symptom_card.pack(fill="x", padx=10, pady=6)
    
    def create_symptom_button(self, symptom, index):
        """Create a clickable symptom card using SymptomCard component"""
        is_selected = (self.selected_symptom == symptom)
        explanation = explain_symptom(symptom)
        
        symptom_card = SymptomCard(
            self.symptom_scroll_frame,
            symptom=symptom,
            explanation=explanation,
            is_selected=is_selected,
            on_click=lambda s=symptom: self.on_symptom_click(s),
            on_confirm=lambda s=symptom: self.confirm_symptom(s)
        )
        symptom_card.pack(fill="x", padx=10, pady=6)
        
        self.symptom_buttons.append(symptom_card)
    
    def show_completion_summary(self):
        """Show detailed completion summary in symptom panel"""
        # Hide skip button when diagnosis is complete
        if self.symptom_header.action_btn:
            self.symptom_header.action_btn.pack_forget()
        
        # Calculate final stats
        sorted_candidates = sorted(
            self.candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top_id, top_prob = sorted_candidates[0] if sorted_candidates else (None, 0.0)
        top_disease_name = self.diseases.get(top_id, {}).get("name", "Unknown") if top_id else "No Diagnosis"
        confidence, gap = calculate_confidence(self.candidates, self.diseases)
        req_hits_top = dynamic_required_hits(self.symptom_map, top_id) if top_id else 0
        hits_top = self.evidence_hits_by_disease.get(top_id, 0) if top_id else 0
        remaining = [d for d, p in sorted_candidates if p > 0.01]
        
        # Stats data with more detail
        stats_data = [
            ("Symptoms Evaluated", f"{len(self.asked)}"),
            ("Evidence-Based Answers", f"{self.answered_with_lr}"),
            ("Final Confidence", f"{confidence:.1%}"),
            ("Confidence Gap", f"{gap:.4f}"),
            ("Top Disease Hits", f"{hits_top}/{req_hits_top}"),
            ("Remaining Candidates", f"{len(remaining)}"),
            ("Final Top Probability", f"{top_prob:.3f}"),
        ]
        
        # Top 3 diseases for summary
        top_diseases = []
        for i, (disease_id, probability) in enumerate(sorted_candidates[:3]):
            disease_info = self.diseases[disease_id]
            hits = self.evidence_hits_by_disease.get(disease_id, 0)
            req_hits = dynamic_required_hits(self.symptom_map, disease_id)
            top_diseases.append((disease_id, disease_info['name'], probability, hits, req_hits))
        
        # Create completion summary using component
        summary = CompletionSummary(
            self.symptom_scroll_frame,
            stats_data=stats_data,
            top_disease_name=top_disease_name,
            top_diseases=top_diseases if top_diseases else None,
            symptom_path=self.symptom_path,
            on_new_diagnosis=self.start_new_diagnosis
        )
        summary.pack(fill="both", expand=True, padx=20, pady=20)
    
    def skip_all_symptoms(self):
        """Skip all current symptoms (shuffle - equivalent to 's' command)"""
        if self.diagnosis_finalized:
            return
        
        # Mark all current symptoms as asked
        for symptom in self.current_symptoms:
            if symptom not in self.asked:
                self.asked.add(symptom)
        
        self.selected_symptom = None
        self.update_ui()
    
    def on_symptom_click(self, symptom):
        """Handle symptom card click"""
        if symptom in self.asked or self.diagnosis_finalized:
            return
        
        # Toggle selection
        if self.selected_symptom == symptom:
            self.selected_symptom = None
        else:
            self.selected_symptom = symptom
        
        self.update_symptom_panel()
    
    def confirm_symptom(self, symptom):
        """Confirm symptom selection"""
        if symptom != self.selected_symptom or symptom in self.asked:
            return
        
        self.selected_symptom = None
        self.select_symptom(symptom)
    
    def select_symptom(self, symptom):
        """Handle symptom selection"""
        if symptom in self.asked or self.diagnosis_finalized:
            return
        
        # Clear search when symptom is selected
        if self.search_entry:
            self.search_entry.delete(0, "end")
        self.search_query = ""
        if self.search_results_frame:
            self.search_results_frame.pack_forget()
        # Make sure symptom scroll frame is visible again
        self.symptom_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.asked.add(symptom)
        self.symptom_path.append(symptom)  # Track order
        
        # Update cluster strength
        cluster = categorize_symptom(symptom)
        from inference import CLUSTER_BOOST_PER_HIT, CLUSTER_BOOST_MAX
        self.cluster_strength[cluster] = min(
            CLUSTER_BOOST_MAX,
            self.cluster_strength.get(cluster, 0.0) + CLUSTER_BOOST_PER_HIT
        )
        
        # Track evidence hits
        did_map = self.symptom_map.get(symptom, {})
        has_any_lr = False
        for d_id, vals in did_map.items():
            if vals.get('lr_pos') is not None:
                self.evidence_hits_by_disease[d_id] += 1
                has_any_lr = True
        if has_any_lr:
            self.answered_with_lr += 1
        
        # Update posteriors
        prev_top = max(self.candidates.values()) if self.candidates else 0.0
        self.candidates = update_posteriors_positive(
            self.candidates,
            symptom,
            self.symptom_map,
            self.cluster_strength,
            self.scarcity_boosts
        )
        new_top = max(self.candidates.values()) if self.candidates else 0.0
        
        # Track low gain
        if new_top - prev_top < 0.05:
            self.consecutive_low_gain += 1
        else:
            self.consecutive_low_gain = 0
        
        # Update UI
        self.update_ui()
    
    def update_diagnosis_panel(self):
        """Update diagnosis results panel"""
        # Clear existing cards
        for widget in self.diagnoses_scroll_frame.winfo_children():
            widget.destroy()
        self.diagnosis_cards = []
        
        if not self.candidates:
            return
        
        # Calculate confidence
        confidence, gap = calculate_confidence(self.candidates, self.diseases)
        
        # Update confidence display using component method
        self.confidence_indicator.update_confidence(confidence)
        
        # Get top diagnoses
        sorted_candidates = sorted(
            self.candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Show all diagnoses with probability > 0.001, or top 10, whichever is less
        top_diseases = [(d, p) for d, p in sorted_candidates if p > 0.001][:10]
        
        for i, (disease_id, probability) in enumerate(top_diseases):
            disease_info = self.diseases[disease_id]
            hits = self.evidence_hits_by_disease.get(disease_id, 0)
            req_hits = dynamic_required_hits(self.symptom_map, disease_id)
            self.create_diagnosis_card(disease_info, probability, i + 1, gap if i == 0 else None, hits, req_hits)
    
    def create_diagnosis_card(self, disease_info, probability, rank, gap=None, hits=0, req_hits=0):
        """Create a card for a diagnosis using DiagnosisCard component"""
        diagnosis_card = DiagnosisCard(
            self.diagnoses_scroll_frame,
            rank=rank,
            disease_name=disease_info["name"],
            probability=probability,
            severity=disease_info.get('triage_severity', None),
            hits=hits,
            req_hits=req_hits,
            description=disease_info.get("description", None)
        )
        diagnosis_card.pack(fill="x", padx=10, pady=6)
        
        self.diagnosis_cards.append(diagnosis_card)
    
    def check_convergence(self):
        """Check if diagnosis should be finalized"""
        if self.diagnosis_finalized:
            return
        
        sorted_c = sorted(self.candidates.items(), key=lambda x: x[1], reverse=True)
        if not sorted_c:
            return
        
        top_id, top_prob = sorted_c[0]
        remaining = [d for d, p in sorted_c if p > 0.01]
        
        confidence, gap = calculate_confidence(self.candidates, self.diseases)
        req_hits_top = dynamic_required_hits(self.symptom_map, top_id)
        hits_top = self.evidence_hits_by_disease.get(top_id, 0)
        
        # Update status using component method
        symptoms_count = len(self.asked)
        status_text = f"{symptoms_count} symptoms · {hits_top}/{req_hits_top} hits · {confidence:.0%} confidence"
        self.symptom_header.update_status(status_text)
        
        # Check convergence criteria
        top_posterior = max(self.candidates.values()) if self.candidates else 0.0
        
        if hits_top >= req_hits_top and top_posterior >= EARLY_FINALIZE_TOPP:
            self.diagnosis_finalized = True
            self.update_ui()
            return
        
        if (confidence >= SUCCESS_CONFIDENCE and self.answered_with_lr >= MIN_EVIDENCE_ANSWERS) or len(remaining) <= 2:
            self.diagnosis_finalized = True
            self.update_ui()
            return
        
        if self.consecutive_low_gain >= 2:
            self.diagnosis_finalized = True
            self.update_ui()
            return
        
        # Check if no more symptoms
        next_symptoms = select_next_symptoms(
            self.candidates,
            self.symptom_map,
            self.asked,
            top_n=1,
            cluster_strength=self.cluster_strength,
            scarcity_boosts=self.scarcity_boosts
        )
        if not next_symptoms:
            self.diagnosis_finalized = True
            self.update_ui()
    
    def show_error(self, message):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error")
        dialog.geometry("400x150")
        dialog.configure(fg_color=COLORS["bg_medium"])
        
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["danger"],
            wraplength=350
        )
        label.pack(pady=30)
        
        btn = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            fg_color=COLORS["accent"]
        )
        btn.pack(pady=10)


def main():
    """Main entry point"""
    try:
        parser = argparse.ArgumentParser(description="IATRO Frontend - Pediatric Diagnostic System")
        parser.add_argument("--db", type=str, default="pediatric.db", help="Path to pediatric.db")
        args = parser.parse_args()
        
        app = DiagnosticApp(db_path=args.db)
        app.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"Fatal error: {e}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        # Try to show error dialog if GUI is available
        try:
            import tkinter.messagebox as mb
            mb.showerror("IATRO Error", error_msg)
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

