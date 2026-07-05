import requests

from app.config import EMAIL_FROM, FRONTEND_URL, RESEND_API_KEY

DISCORD_URL = "https://discord.gg/saFBWEDUb8"
OWNER_EMAIL = "SanityRCinfo@gmail.com"


def send_email(to_email: str, subject: str, text: str, html: str):
   if not RESEND_API_KEY:
       print("EMAIL NOT SENT: RESEND_API_KEY missing")
       return False

   payload = {
       "from": EMAIL_FROM,
       "to": [to_email],
       "subject": subject,
       "text": text,
       "html": html,
   }

   try:
       res = requests.post(
           "https://api.resend.com/emails",
           headers={
               "Authorization": f"Bearer {RESEND_API_KEY}",
               "Content-Type": "application/json",
           },
           json=payload,
           timeout=20,
       )

       if res.status_code >= 400:
           print("RESEND EMAIL FAILED:", res.status_code, res.text)
           return False

       print(f"EMAIL SENT TO: {to_email}")
       return True

   except Exception as e:
       print("EMAIL ERROR:", repr(e))
       return False


def send_license_email(to_email: str, license_key: str):
   activation_link = f"{FRONTEND_URL}/register?license={license_key}"

   text = f"""
Welcome to Sanity RC!

Your license key:
{license_key}

Activate your license:
{activation_link}

Join our Discord:
{DISCORD_URL}

- Sanity RC
"""

   html = f"""
   <div style="background:#080A0F;padding:40px;font-family:Arial;color:white;">
     <div style="max-width:650px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:24px;overflow:hidden;">
       <div style="background:linear-gradient(135deg,#ef0000,#7f0d12);padding:34px;text-align:center;">
         <h1 style="margin:0;font-size:38px;">Sanity RC</h1>
         <p style="color:#fee2e2;">Rust Console Control Panel</p>
       </div>

       <div style="padding:34px;">
         <h2>Your license is ready 🎉</h2>
         <p style="color:#9ca3af;">Use this key to activate your account.</p>

         <div style="margin:24px 0;padding:20px;background:#080A0F;border:1px solid #374151;border-radius:16px;text-align:center;">
           <p style="color:#9ca3af;font-size:13px;">LICENSE KEY</p>
           <div style="font-size:24px;color:#f87171;font-weight:900;">{license_key}</div>
         </div>

         <div style="text-align:center;margin-top:30px;">
           <a href="{activation_link}" style="background:#ef0000;color:white;text-decoration:none;padding:16px 28px;border-radius:14px;font-weight:900;display:inline-block;">
             Activate License
           </a>

           <a href="{DISCORD_URL}" style="background:#5865F2;color:white;text-decoration:none;padding:16px 28px;border-radius:14px;font-weight:900;display:inline-block;margin-left:10px;">
             Join Discord
           </a>
         </div>
       </div>
     </div>
   </div>
   """

   return send_email(to_email, "Your Sanity RC License Is Ready", text, html)


def send_waitlist_email(to_email: str):
   text = f"""
You're on the Sanity RC Early Access Waitlist!

Thanks for joining.

You'll receive updates when early access opens.

Visit:
{FRONTEND_URL}

Join our Discord:
{DISCORD_URL}

- Sanity RC
"""

   html = f"""
   <div style="background:#080A0F;padding:40px;font-family:Arial;color:white;">
     <div style="max-width:650px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:24px;overflow:hidden;">
       <div style="background:linear-gradient(135deg,#ef0000,#7f0d12);padding:34px;text-align:center;">
         <h1 style="margin:0;font-size:38px;">You're on the Waitlist</h1>
         <p style="color:#fee2e2;">Sanity RC Early Access</p>
       </div>

       <div style="padding:34px;">
         <h2>Welcome to Early Access 🎉</h2>

         <p style="color:#9ca3af;line-height:1.7;">
           Thanks for joining the official <b style="color:white;">Sanity RC Early Access Waitlist</b>.
           You’ll be one of the first server owners notified when Founder Access opens.
         </p>

         <div style="margin:26px 0;padding:22px;background:#080A0F;border:1px solid #374151;border-radius:16px;">
           <p style="font-size:18px;font-weight:900;">What happens next?</p>
           <p>✅ Priority early access</p>
           <p>✅ Founder pricing updates</p>
           <p>✅ Feature previews</p>
           <p>✅ Launch notifications</p>
           <p>✅ Discord community access</p>
         </div>

         <div style="text-align:center;margin-top:30px;">
           <a href="{FRONTEND_URL}" style="background:#ef0000;color:white;text-decoration:none;padding:16px 28px;border-radius:14px;font-weight:900;display:inline-block;">
             Visit SanityRC
           </a>

           <a href="{DISCORD_URL}" style="background:#5865F2;color:white;text-decoration:none;padding:16px 28px;border-radius:14px;font-weight:900;display:inline-block;margin-left:10px;">
             Join Discord
           </a>
         </div>

         <p style="color:#6b7280;font-size:13px;text-align:center;margin-top:30px;">
           You received this email because you joined the Sanity RC waitlist.
         </p>
       </div>
     </div>
   </div>
   """

   return send_email(
       to_email,
       "🎉 You're on the Sanity RC Early Access Waitlist",
       text,
       html,
   )


def send_owner_waitlist_notification(email: str, discord: str | None):
   text = f"""
New Sanity RC Waitlist Signup

Email: {email}
Discord: {discord or "Not provided"}
"""

   html = f"""
   <div style="background:#080A0F;padding:30px;font-family:Arial;color:white;">
     <div style="max-width:600px;margin:auto;background:#111827;border:1px solid #1f2937;border-radius:20px;padding:30px;">
       <h1 style="color:#f87171;">🚀 New Waitlist Signup</h1>
       <p><b>Email:</b> {email}</p>
       <p><b>Discord:</b> {discord or "Not provided"}</p>
     </div>
   </div>
   """

   return send_email(
       OWNER_EMAIL,
       "🚀 New Sanity RC Waitlist Signup",
       text,
       html,
   )