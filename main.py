from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.dashboard import router as dashboard_router
from app.routes.server import router as server_router
from app.routes.players import router as players_router
from app.routes.logs import router as logs_router
from app.routes.console import router as console_router
from app.routes.files import router as files_router
from app.routes.auth import router as auth_router
from app.database import Base, engine
from app.routes.stats import router as stats_router
from app.routes.payments import router as payments_router
from app.routes.paypal import router as paypal_router
from app.routes.waitlist import router as waitlist_router
from app.routes.connected_server import router as connected_server_router
from app.routes.reports import router as reports_router
from app.routes.rcon import router as rcon_router
from app.routes.live import router as live_router

app = FastAPI(title="SANITY2X Private API")
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://sanityrc.com",
        "https://www.sanityrc.com",
        "https://sanityrc-panel.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(server_router)
app.include_router(players_router)
app.include_router(logs_router)
app.include_router(console_router)
app.include_router(files_router)
app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(payments_router)
app.include_router(paypal_router)
app.include_router(waitlist_router)
app.include_router(connected_server_router)
app.include_router(reports_router)
app.include_router(rcon_router)
app.include_router(live_router)




@app.get("/")
def home():
    return {"status": "Backend online", "name": "SANITY2X API"}