import flet as ft
from custom_controls import custom_text_button
import riot_logic
import wizard_logic

HEXTECK_GOLD = "#D4AF37"
BLOOD_RED = "#AD0000"
OVERWATCH_BLUE = "#218FFE"

RANKS_VALORANT =["-", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"]
RANKS_LOL =["-", "Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Master", "Grandmaster", "Challenger"]
RANKS_OW =["-", "Unranked", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grand Master", "Champion", "Top 500"]
REGIONS_LOL =["-", "NA", "EUW", "EUNE", "KR", "JP", "OCE", "LAN", "LAS", "TR", "BR", "SEA", "MENA"]

def wizard(page: ft.Page):

    instructions_text = ft.Text("Follow these instructions to set-up your profile successfully.", weight=ft.FontWeight.BOLD, color=HEXTECK_GOLD, size=20)

    name_input = ft.TextField(
        label="Profile Name (e.g. My Main)", 
        width=280, 
        color=ft.Colors.WHITE, 
        border_color=ft.Colors.WHITE,
        border_radius=ft.border_radius.only(top_left=12, top_right=12)
    )

    region_dd = ft.Dropdown(
        color=ft.Colors.WHITE,
        border_color=ft.Colors.WHITE,
        hint_text="Select Your Region",
        width=280,
        visible=False,
        options=[ft.dropdown.Option(region) for region in REGIONS_LOL]
    )

    rank_dd = ft.Dropdown(
        color=ft.Colors.WHITE,
        border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
        border_color=ft.Colors.WHITE,
        hint_text="Select Your Rank",
        width=280,
        options=[ft.dropdown.Option(rank) for rank in RANKS_LOL],
    )

    def handle_game_change():
        selected_game = game_dd.value

        if selected_game == "League of Legends":
            region_dd.visible = True
            rank_dd.options = [ft.dropdown.Option(rank) for rank in RANKS_LOL]
            game_dd.border_color = HEXTECK_GOLD
            rank_dd.border_color = HEXTECK_GOLD
            region_dd.border_color = HEXTECK_GOLD
            name_input.border_color = HEXTECK_GOLD
            
        elif selected_game == "Valorant":
            region_dd.visible = False
            rank_dd.options =[ft.dropdown.Option(rank) for rank in RANKS_VALORANT]
            game_dd.border_color = BLOOD_RED
            rank_dd.border_color = BLOOD_RED
            name_input.border_color = BLOOD_RED

        elif selected_game == "Overwatch":
            region_dd.visible = False
            rank_dd.options =[ft.dropdown.Option(rank) for rank in RANKS_OW]
            game_dd.border_color = OVERWATCH_BLUE
            rank_dd.border_color = OVERWATCH_BLUE
            name_input.border_color = OVERWATCH_BLUE

        rank_dd.value = "Select Your Rank"
        region_dd.value = "Select Your Region"

        region_dd.update()
        rank_dd.update()
        game_dd.update()
        name_input.update()

    game_dd = ft.Dropdown(
        color=ft.Colors.WHITE,
        hint_text="Select Game",
        border_color=ft.Colors.WHITE,
        value="-",
        width=280,
        options=[
            ft.dropdown.Option("Valorant"),
            ft.dropdown.Option("League of Legends"),
            ft.dropdown.Option("Overwatch")
        ],
        on_select=handle_game_change
    )

    def update_btn_ui(msg, disabled, btn_text=None):
        instructions_text.value = msg
        
        if btn_text:
            action_btn.content.value = btn_text #type: ignore
            
        action_btn.disabled = disabled 
        action_btn.opacity = 0.5 if disabled else 1.0 
        page.update()

    # 3. The Click Handler
    async def on_action_click():
        service = "riot" if game_dd.value in ["League of Legends", "Valorant"] else "bnet"
        
        current_text = action_btn.content.value #type: ignore
        
        if "Step 1" in current_text or "Try again" in current_text:
            # Execute Step 1
            await wizard_logic.start_auth_process(service, update_btn_ui)
        else:
            # Execute Step 2
            await wizard_logic.validate_and_save(
                page=page,
                name=name_input.value,
                service=service,
                game=str(game_dd.value),
                rank=str(rank_dd.value),
                region=str(region_dd.value) if region_dd.visible else "",
                status_callback=update_btn_ui
            )

    action_btn = custom_text_button(
        action=lambda: page.run_task(on_action_click), 
        text="Step 1: Open Client", 
        width=280, 
        active_color=BLOOD_RED
    )

    async def cancel_button():
        instructions_text.value = "Redirecting... Please wait."
        page.update()
        await riot_logic.force_kill_all_services()
        page.go("/home")

    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        content=ft.Container(
            expand=True,
            blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
            content=ft.Column(
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        content=instructions_text,
                        alignment=ft.Alignment.CENTER,
                        margin=ft.Margin.only(bottom=40)
                    ),
                    name_input,
                    game_dd,
                    region_dd,
                    rank_dd,
                    ft.Container(
                        margin=ft.margin.only(top=30),
                        alignment=ft.Alignment.CENTER,
                        content=action_btn
                    ),
                    ft.Container(
                        margin=ft.margin.only(top=10),
                        alignment=ft.Alignment.CENTER,
                        content=custom_text_button(lambda: page.run_task(cancel_button), "Cancel", 280, active_color=BLOOD_RED)
                    )
                ]
            )
        )
    )