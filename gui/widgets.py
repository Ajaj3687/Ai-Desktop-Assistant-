import customtkinter as ctk

class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, sender="assistant", **kwargs):
        # Translucent outer container frame
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Configure layout styling depending on the sender
        if sender == "user":
            bubble_fg = "#1f538d"       # Premium dark blue tone
            text_color = "#ffffff"
            align_anchor = "e"         # Pack to the right side
            bubble_anchor = "ne"
            bubble_padding = (60, 10)
        else:
            bubble_fg = "#2e2e2e"       # Premium soft graphite tone
            text_color = "#e5e5e5"
            align_anchor = "w"         # Pack to the left side
            bubble_anchor = "nw"
            bubble_padding = (10, 60)

        # Bubble content container
        self.bubble_inner = ctk.CTkFrame(self, fg_color=bubble_fg, corner_radius=12)
        self.bubble_inner.pack(anchor=bubble_anchor, padx=bubble_padding, pady=4)

        # Text wrapper label with responsive text wraps
        self.label = ctk.CTkLabel(
            self.bubble_inner, 
            text=text, 
            text_color=text_color,
            wraplength=380,            # Wraps lines nicely in the chat view area
            justify="left",
            font=("Segoe UI", 13)
        )
        self.label.pack(padx=12, pady=8)

        # Pack the main bubble widget inside the scrolling thread window
        self.pack(fill="x", anchor=align_anchor)

class StateIndicator(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Display state title
        self.indicator_label = ctk.CTkLabel(
            self, 
            text="● IDLE", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#9e9e9e"
        )
        self.indicator_label.pack(padx=8, pady=2)
        
    def set_state(self, state):
        """Dynamic color updates based on current assistant state."""
        state = state.upper()
        if state == "IDLE":
            self.indicator_label.configure(text="● IDLE", text_color="#9e9e9e")
        elif state == "LISTENING":
            self.indicator_label.configure(text="🎙️ LISTENING...", text_color="#e05252") # Subtle glowing red
        elif state == "PROCESSING":
            self.indicator_label.configure(text="⚡ PROCESSING...", text_color="#f1c40f") # Bright energy yellow
        elif state == "SPEAKING":
            self.indicator_label.configure(text="🔊 SPEAKING...", text_color="#2ecc71") # Active talking green
        else:
            self.indicator_label.configure(text=f"● {state}", text_color="#9e9e9e")
