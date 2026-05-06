import asyncio
import riot_logic

async def start_auth_process(service: str, status_callback):
    status_callback("Closing active sessions...", disabled=True)

    await riot_logic.request_graceful_shutdown(service)
    await riot_logic.force_kill_all_services()
    await riot_logic.prepare_fresh_client(service)

    status_callback(
        msg="Client Opened. Log-in (Make sure to check \"Stay Signed-in\" box), then click \"Step 2.\"", 
        disabled=False, 
        btn_text="Step 2: Complete & Validate"
    )

async def validate_and_save(page, name: str, service: str, game: str, rank: str, region: str, status_callback):
    if not name or name.strip() == "":
        status_callback("Profile Name Cannot be Empty.", disabled=False)
        return
    
    status_callback("Validating and Saving to Disk (4s)...", disabled=True)

    # FIX: Synchronous flush
    await riot_logic.request_graceful_shutdown(service)

    await riot_logic.force_kill_all_services()

    pid = await riot_logic.validate_and_capture_profile(
        name=name.strip(),
        service=service,
        game=game,
        rank=rank,
        region=region
    )

    if pid:
        status_callback("Redirecting...", disabled=True)
        await asyncio.sleep(1.0)
        page.go("/home")

    else:
        status_callback("Auth corrupted. Check \"Stay Signed-in\"", disabled=True)
        await asyncio.sleep(2.0)
        await riot_logic.request_graceful_shutdown(service)
        await riot_logic.force_kill_all_services()
        await riot_logic.prepare_fresh_client(service)
        
        status_callback(
            msg="Client Reopened. Please try again.", 
            disabled=False, 
            btn_text="Step 1: Try again"
        )