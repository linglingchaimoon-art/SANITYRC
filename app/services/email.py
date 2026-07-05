import smtplib
from email.message import EmailMessage

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM


from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, FRONTEND_URL


def send_email(to_email: str, subject: str, text: str, html: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        print("EMAIL NOT SENT: SMTP is not configured")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT), timeout=10) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)

    print(f"EMAIL SENT TO: {to_email}")
    return True


def send_license_email(to_email: str, license_key: str):
    activation_link = f"{FRONTEND_URL}/register?license={license_key}"

    text = f"""
Welcome to Sanity RC!

Thank you for your purchase.

Your license key:
{license_key}

Activate your license here:
{activation_link}

- Sanity RC
"""

    html = f"""
    <html>
      <body style="margin:0; padding:0; background:#080A0F; font-family:Arial, sans-serif; color:#ffffff;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#080A0F; padding:40px 0;">
          <tr>
            <td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="background:#111827; border:1px solid #1f2937; border-radius:24px; overflow:hidden;">
                <tr>
                  <td style="background:linear-gradient(135deg,#ef0000,#7f0d12); padding:32px; text-align:center;">
                    <div style="display:inline-block; background:#ef0000; color:#fff; font-size:28px; font-weight:900; padding:16px 18px; border-radius:18px;">RC</div>
                    <h1 style="margin:20px 0 0; font-size:34px; font-weight:900;">Welcome to Sanity RC</h1>
                    <p style="margin:10px 0 0; color:#fee2e2; font-size:16px;">Your Rust Console panel license is ready.</p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:32px;">
                    <h2 style="margin:0; font-size:24px;">Thank you for your purchase.</h2>
                    <p style="color:#9ca3af; line-height:1.6; font-size:16px;">
                      Use the license key below to activate your Sanity RC account.
                    </p>

                    <div style="margin:26px 0; padding:20px; background:#080A0F; border:1px solid #374151; border-radius:16px; text-align:center;">
                      <p style="margin:0 0 8px; color:#9ca3af; font-size:13px; text-transform:uppercase; letter-spacing:1px;">License Key</p>
                      <div style="font-size:24px; color:#f87171; font-weight:900; letter-spacing:1px;">{license_key}</div>
                    </div>

                    <div style="text-align:center; margin:30px 0;">
                      <a href="{activation_link}" style="background:#ef0000; color:white; text-decoration:none; padding:16px 28px; border-radius:14px; font-weight:900; display:inline-block;">
                        Activate License
                      </a>
                    </div>

                    <p style="color:#9ca3af; line-height:1.6; font-size:14px;">
                      If the button does not work, copy this link into your browser:<br>
                      <span style="color:#f87171;">{activation_link}</span>
                    </p>

                    <hr style="border:none; border-top:1px solid #1f2937; margin:28px 0;">

                    <p style="color:#6b7280; font-size:13px; text-align:center;">
                      Sanity RC • Rust Console Control Panel
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    return send_email(
        to_email,
        "Your Sanity RC License Is Ready",
        text,
        html,
    )


def send_waitlist_email(to_email: str):
    text = f"""
You're on the Sanity RC Early Access Waitlist!

Thanks for joining.

You'll be one of the first to hear when Founder Access opens.

What happens next:
- Priority early access
- Founder pricing updates
- Feature previews
- Launch notifications

Visit:
{FRONTEND_URL}

- Sanity RC
"""

    html = f"""
    <html>
      <body style="margin:0; padding:0; background:#080A0F; font-family:Arial, sans-serif; color:#ffffff;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#080A0F; padding:40px 0;">
          <tr>
            <td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="background:#111827; border:1px solid #1f2937; border-radius:24px; overflow:hidden;">
                <tr>
                  <td style="background:linear-gradient(135deg,#ef0000,#7f0d12); padding:34px; text-align:center;">
                    <div style="display:inline-block; background:#ef0000; color:#fff; font-size:28px; font-weight:900; padding:16px 18px; border-radius:18px;">RC</div>
                    <h1 style="margin:20px 0 0; font-size:34px; font-weight:900;">You're on the Waitlist</h1>
                    <p style="margin:10px 0 0; color:#fee2e2; font-size:16px;">Sanity RC Early Access</p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:34px;">
                    <h2 style="margin:0; font-size:24px;">Welcome to Early Access 🎉</h2>

                    <p style="color:#9ca3af; line-height:1.7; font-size:16px;">
                      Thanks for joining the official <strong style="color:#ffffff;">Sanity RC Early Access Waitlist</strong>.
                      You’ll be one of the first server owners notified when Founder Access opens.
                    </p>

                    <div style="margin:26px 0; padding:22px; background:#080A0F; border:1px solid #374151; border-radius:16px;">
                      <p style="margin:0 0 14px; color:#ffffff; font-size:18px; font-weight:900;">What happens next?</p>
                      <p style="margin:8px 0; color:#d1d5db;">✅ Priority early access</p>
                      <p style="margin:8px 0; color:#d1d5db;">✅ Founder pricing updates</p>
                      <p style="margin:8px 0; color:#d1d5db;">✅ Feature previews</p>
                      <p style="margin:8px 0; color:#d1d5db;">✅ Launch notifications</p>
                    </div>

                    <div style="text-align:center; margin:30px 0;">
                      <a href="{FRONTEND_URL}" style="background:#ef0000; color:white; text-decoration:none; padding:16px 28px; border-radius:14px; font-weight:900; display:inline-block;">
                        Visit SanityRC
                      </a>
                    </div>

                    <p style="color:#6b7280; font-size:13px; text-align:center;">
                      You received this email because you joined the Sanity RC waitlist.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
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
    <html>
      <body style="font-family:Arial, sans-serif; background:#080A0F; color:white; padding:30px;">
        <div style="max-width:600px; margin:auto; background:#111827; border:1px solid #1f2937; border-radius:20px; padding:30px;">
          <h1 style="color:#f87171;">🚀 New Waitlist Signup</h1>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Discord:</strong> {discord or "Not provided"}</p>
        </div>
      </body>
    </html>
    """

    return send_email(
        SMTP_USER,
        "🚀 New Sanity RC Waitlist Signup",
        text,
        html,
    )