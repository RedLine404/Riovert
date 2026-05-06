import flet as ft
from custom_controls import on_hover, custom_text_button, custom_card, sidebar
import riot_logic
from riot_logic import THIRD_PARTY_APPS
import asyncio
import os

HEXTECK_GOLD = "#D4AF37"
BLOOD_RED = "#AD0000"
OVERWATCH_BLUE = "#218FFE"

async def trigger_play_sequence(page: ft.Page, state, pid: str, game: str):
    if state.is_switching:
        return 

    state.is_switching = True

    helper_key = state.helper_options.get(state.selected_helper_display)
    
    await riot_logic.play_profile(
        pid=pid, 
        helper_app_key=helper_key,
        status_callback=state.update_ticker
    )
    
    state.is_switching = False

def home_page(page):
    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            align=ft.Alignment.CENTER,
            spacing=50,
            controls=[
                custom_card(page, "Riot Games", "Riot Games.jpg", active_color=BLOOD_RED, target_page="/riot"),
                custom_card(page, "Battle.net", "Battlenet.jpg", active_color=OVERWATCH_BLUE, target_page="/bnet"),
                custom_card(page, "Add New Profile", "new_profile.png", action=lambda: page.go("/wizard"))
            ]
        )
    )

def riot_page(page, state):

    # ----- Helper Apps -----
    
    def handle_helper_change(e):
        state.selected_helper_display = e.control.value
        state.save_config()

    helper_dd = ft.Dropdown(
        options=[ft.dropdown.Option(helper) for helper in state.helper_options.keys()],
        value=state.selected_helper_display,
        on_select=handle_helper_change,
        width=250,
        border_color=BLOOD_RED,
        bgcolor=ft.Colors.TRANSPARENT,
        fill_color=ft.Colors.TRANSPARENT,
        filled=True,
        border_radius=12,
    )

    animated_helper_dd = ft.Container(
        content=helper_dd,
        bgcolor=ft.Colors.with_opacity(0.09, "#FFFFFF"),
        border_radius=12,
        on_hover=lambda e: on_hover(e, True)
    )

    async def restart_active_helper():
        app_key = state.helper_options.get(state.selected_helper_display)
        if app_key:
            state.update_ticker(f"[LOG] SWITCHING TO HELPER APP '{state.selected_helper_display}'.")
            await riot_logic.kill_helpers(app_key)
            if riot_logic.launch_third_party_app(app_key):
                state.update_ticker(f"[LOG]{helper_dd.value} IS ONLINE.")
            else:
                state.update_ticker(f"[LOG] FAILD TO LAUNCH '{helper_dd.value}'.")

    async def kill_active_helper(e):
        app_key = state.helper_options.get(state.selected_helper_display)
        if app_key:
            state.update_ticker(f"[LOG] CLOSING '{state.selected_helper_display}'.")
            await riot_logic.kill_helpers(app_key)
            state.update_ticker(f"[LOG] '{state.selected_helper_display}' CLOSED.")
        else:
            state.update_ticker(f"[LOG] FAILED TO CLOSE '{state.selected_helper_display}'.")

    helper_termination_button = ft.Container(
        content=custom_text_button(kill_active_helper, f"Close Current Helper", 250, active_color=BLOOD_RED)
    )
    helper_switch_button = ft.Container(
        content=custom_text_button(restart_active_helper, "Switch/Restart Helper", width=250, active_color=HEXTECK_GOLD)
    )

    # ----- End of Helper Apps -----

    profiles = riot_logic.get_profiles_by_service("riot")
    dynamic_cards: list[ft.Control]=[]

    if not profiles:
        dynamic_cards.append(ft.Text("NO RIOT PROFILES FOUND.", size=20, weight=ft.FontWeight.BOLD, color="white"))

    else:
        lol_color_active = False
        for pid, data in profiles.items():
            if data["game"] == "lol" and data["region"] == "EUW":
                img_path = "LOLeuw.png"
                lol_color_active = True
            elif data["game"] == "lol" and data["region"] == "EUNE":
                img_path = "LOLeune.png"
                lol_color_active = True
            else:
                img_path = "Valorant.jpg"
            
            display_name = f"[{data['region']}] {data['name']}" if data.get('region') else data['name']
            action_func = lambda p=pid, g=data["game"]: page.run_task(trigger_play_sequence, page, state, p, g)

            card = custom_card(page, display_name, img_path, action=action_func, active_color=HEXTECK_GOLD if lol_color_active == True else "#FF0000")
            
            edit_button = custom_text_button(lambda e, p=pid: page.go(f"/edit/{p}"), "Edit", width=250)

            card_column = ft.Column(
                controls=[
                    card,
                    edit_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                margin=ft.Margin.only(bottom=10)
            )

            dynamic_cards.append(card_column)
        new_profile_card = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            margin=ft.Margin.only(bottom=60),
            controls=[custom_card(page, "Add New Profile", "new_profile.png", action=lambda: page.go("/wizard"))]
        )
        dynamic_cards.append(new_profile_card)


    main_content = ft.Container(
        expand=True,
        content=ft.Row(
            wrap=True,
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50,
            run_spacing=50,
            controls=dynamic_cards
        )
    )

    helper_toolbar = ft.Container(
        width=265,
        margin=ft.Margin.only(bottom=10, top=10),
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            controls=[
                # TOP ITEMS
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Actieve Helper:", color=HEXTECK_GOLD, weight=ft.FontWeight.BOLD),
                        animated_helper_dd,
                    ]
                ),
                
                # BOTTOM ITEMS
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        helper_termination_button,
                        helper_switch_button
                    ]
                )
            ]
        )
    )
    page.update()

    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
        content=ft.Row(
            expand=True,
            controls=[
                sidebar(page),
                main_content,
                ft.Container(width=1, bgcolor=ft.Colors.with_opacity(0.3, HEXTECK_GOLD), margin=ft.Margin.only(bottom=10, top=10),),
                helper_toolbar
            ],
        )
    )

def bnet_page(page, state):
    profiles = riot_logic.get_profiles_by_service("bnet")

    dynamic_cards: list[ft.Control] = []

    if not profiles:
        dynamic_cards.append(ft.Text("NO BNET PROFILES FOUND.", size=20, weight=ft.FontWeight.BOLD, color="white"))

    else:
        for pid, data in profiles.items():
            display_name = data["name"]

            action_func = lambda p=pid, g=data["game"]: page.run_task(trigger_play_sequence, page, state, p, g)

            card = custom_card(page, display_name, "Overwatch.jpg", action=action_func, active_color=OVERWATCH_BLUE)
            
            edit_button = custom_text_button(lambda e, p=pid: page.go(f"/edit/{p}"), "Edit", width=250)
            
            # FIX: Wrap them in a Column so they stack vertically!
            card_column = ft.Column(
                controls=[
                    card,
                    edit_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                margin=ft.Margin.only(bottom=10)
            )
            
            # Append the grouped column instead of individual pieces
            dynamic_cards.append(card_column)
        new_profile_card = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            margin=ft.Margin.only(bottom=60),
            controls=[custom_card(page, "Add New Profile", "new_profile.png", action=lambda: page.go("/wizard"))]
        )
        dynamic_cards.append(new_profile_card)

    main_content = ft.Container(
        expand=True,
        content=ft.Row(
            wrap=True,
            scroll=ft.ScrollMode.HIDDEN,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=50,
            run_spacing=50,
            controls=dynamic_cards
        )
    )
    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
        content=ft.Row(
            expand=True,
            controls=[
                sidebar(page), 
                main_content   
            ],
        )
    )

def settings_page(page: ft.Page):
    
    status_text = ft.Text("SYSTEM DIAGNOSTICS", size=20, weight=ft.FontWeight.BOLD, color=HEXTECK_GOLD, text_align=ft.TextAlign.CENTER)

    def update_status(msg, color=HEXTECK_GOLD):
        status_text.value = msg
        status_text.color = color
        page.update()

    def validate_all(e):
        profiles = riot_logic.get_all_profiles()
        if not profiles:
            update_status("DIAGNOSTICS: NO PROFILES CONFIGURED.", ft.Colors.RED_400)
            return
            
        results =[]
        for pid, data in profiles.items():
            is_valid = riot_logic.validate_saved_profile(pid)
            if not is_valid:
                tracker_path = os.path.join(riot_logic.RIOT_CLIENT_DIR if data["service"] == "riot" else riot_logic.BNET_ROAMING_DIR, "active_profile.txt")
                try:
                    if open(tracker_path).read().strip() == pid:
                        is_valid = riot_logic.validate_active_auth(data["service"])
                except:
                    pass
            
            status = "VALID" if is_valid else "CORRUPT"
            results.append(f"{data['name']}: {status}")
            
        update_status(" | ".join(results))

    async def wipe_system(e):
        update_status("INITIATING WIPE PROTOCOL...")

        await riot_logic.request_graceful_shutdown("riot")
        await riot_logic.request_graceful_shutdown("bnet")
        await asyncio.sleep(2.0)
        await riot_logic.force_kill_all_services()

        profiles = riot_logic.get_all_profiles()
        for pid in list(profiles.keys()):
            riot_logic.delete_profile(pid)
            
        update_status("DATA WIPED. RETURNING TO HOME...", ft.Colors.GREEN_400)
        await asyncio.sleep(1.5)
        page.go("/home")

    return ft.Container(
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
        blur=ft.Blur(50, 50, ft.BlurTileMode.CLAMP),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            controls=[
                ft.Container(
                    content=status_text,
                    alignment=ft.Alignment.CENTER,
                    margin=ft.Margin.only(bottom=20)
                ),
                custom_text_button(validate_all, "Check & Validate All Profiles", 280, active_color=HEXTECK_GOLD),
                custom_text_button(lambda e: page.go("/wizard"), "Re-setup All profiles", 280, active_color=HEXTECK_GOLD),
                custom_text_button(lambda e: page.run_task(wipe_system, e), "Delete ALL Profiles (WIPE)", 280, active_color=BLOOD_RED),
                custom_text_button(lambda e: page.go("/home"), "Return", 280, active_color="#575757")
            ]
        )
    )