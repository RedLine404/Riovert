import flet as ft
import riot_logic
from custom_controls import custom_text_button

HEXTECK_GOLD = "#D4AF37"
BLOOD_RED = "#AD0000"
OVERWATCH_BLUE = "#218FFE"

RANKS_VALORANT = ["-", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"]
RANKS_LOL = ["-", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]
RANKS_OW = ["-", "Unranked", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grand Master", "Champion", "Top 500"]
REGIONS_LOL = ["NA", "EUW", "EUNE", "KR", "JP", "OCE", "LAN", "LAS", "TR", "BR", "SEA", "MENA"]

def profiles_edit(page: ft.Page, state, pid: str):
    # 1. FETCH PROFILE DATA
    profiles = riot_logic.get_all_profiles()
    
    if pid not in profiles:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("ERROR: PROFILE NOT FOUND.", color=ft.Colors.RED_400, size=24, weight=ft.FontWeight.BOLD),
                    custom_text_button(lambda e: page.go("/home"), "Return Home", 250)
                ]
            )
        )
        
    profile_data = profiles[pid]
    current_name = profile_data.get("name", "")
    current_game = profile_data.get("game", "")
    current_rank = profile_data.get("rank", "")
    current_region = profile_data.get("region", "")
    current_service = profile_data.get("service", "")

    # Determine which ranks to show based on the game
    rank_options = RANKS_VALORANT
    if current_game == "lol":
        rank_options = RANKS_LOL
        theme_color = HEXTECK_GOLD
    elif current_game == "overwatch":
        rank_options = RANKS_OW
        theme_color = OVERWATCH_BLUE
    else:
        theme_color = BLOOD_RED

    # 2. UI ELEMENTS
    status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    name_input = ft.TextField(
        label="Profile Name", 
        value=current_name,
        width=280,
        color=ft.Colors.WHITE,
        border_color=theme_color,
        bgcolor="#121212",
        fill_color=ft.Colors.TRANSPARENT,
        filled=True,
        border_radius=ft.border_radius.only(top_left=12, top_right=12)
    )

    rank_dd = ft.Dropdown(
        label="Account Rank",
        value=current_rank,
        options=[ft.dropdown.Option(r) for r in rank_options],
        width=280,
        color=ft.Colors.WHITE,
        border_color=theme_color,
        bgcolor="#121212",
        fill_color=ft.Colors.TRANSPARENT,
        filled=True,
        border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12)
    )

    region_dd = ft.Dropdown(
        label="Account Region",
        value=current_region if current_region else "EUW",
        options=[ft.dropdown.Option(r) for r in REGIONS_LOL],
        width=280,
        color=ft.Colors.WHITE,
        border_color=HEXTECK_GOLD,
        bgcolor=HEXTECK_GOLD,
        fill_color=ft.Colors.TRANSPARENT,
        filled=True,
        visible=(current_game == "lol")
    )
        
    # ACTION FUNCTIONS
    def validate_profile_action(e):
        is_valid = riot_logic.validate_saved_profile(pid)
        if is_valid:
            status_text.value = "STATUS: PROFILE IS VALID."
            status_text.color = ft.Colors.GREEN_400
        else:
            status_text.value = "STATUS: PROFILE CORRUPT OR MISSING."
            status_text.color = ft.Colors.RED_400
        page.update()

    def resetup_profile(e):
        riot_logic.delete_profile(pid)
        page.go("/wizard") 

    def save_changes(e):
        new_region = region_dd.value if current_game == "lol" else ""
        
        riot_logic.save_profile(
            pid=pid,
            name=name_input.value,
            service=current_service,
            game=current_game,
            rank=rank_dd.value,
            region=str(new_region)
        )
        status_text.value = "STATUS: CHANGES SAVED SUCCESSFULLY!"
        status_text.color = HEXTECK_GOLD
        page.update()
        page.go(f"/{current_service}")

    # --- FLET DIALOG LOGIC ---
    def confirm_delete():
        riot_logic.delete_profile(pid)
        page.pop_dialog()
        state.current_service = current_service
        page.go(f"/{current_service}") 

    def cancel_delete(e):
        page.pop_dialog()

    delete_dialog = ft.AlertDialog(
        title=ft.Text("Confirm Deletion", color=ft.Colors.RED_400),
        content=ft.Text(f"Are you sure you want to delete '{current_name}'?\nThis action cannot be undone.", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.with_opacity(0.99, "#121212"),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_delete),
            ft.TextButton("Confirm", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    def prompt_delete():
        page.show_dialog(delete_dialog)

    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
        align=ft.Alignment.CENTER,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Text(f"EDITING: {current_name.upper()}", size=28, weight=ft.FontWeight.BOLD, color=HEXTECK_GOLD),
                status_text,
                ft.Container(height=10), # Spacer
                
                name_input,
                region_dd,
                rank_dd,
                
                ft.Container(height=20), # Spacer
                
                custom_text_button(save_changes, "Save Changes", 280, active_color="#00FF00"),
                custom_text_button(validate_profile_action, "Validate Profile", 280, active_color="#BF00FF"),
                custom_text_button(resetup_profile, "Re-Setup Profile", 280, active_color=HEXTECK_GOLD),
                custom_text_button(prompt_delete, "Delete Profile", 280, active_color=BLOOD_RED),
                
                ft.Container(height=20),
                custom_text_button(lambda: page.go(f"/{current_service}"), "Cancel & Return", 280, active_color="#555555")
            ]
        )
    )