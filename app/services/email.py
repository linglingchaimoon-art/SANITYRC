import smtplib
from email.message import EmailMessage

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM


def send_license_email(to_email: str, license_key: str):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        print("EMAIL NOT SENT: SMTP is not configured")
        return False

    activation_link = f"http://localhost:5173/register?license={license_key}"

    msg = EmailMessage()
    msg["Subject"] = "Your Sanity RC License Is Ready"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(f"""
Welcome to Sanity RC!

Thank you for your purchase.

Your license key:
{license_key}

Activate your license here:
{activation_link}

- Sanity RC
""")

    html = f"""
    <html>
      <body style="margin:0; padding:0; background:#080A0F; font-family:Arial, sans-serif; color:#ffffff;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#080A0F; padding:40px 0;">
          <tr>
            <td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="background:#111827; border:1px solid #1f2937; border-radius:24px; overflow:hidden;">
                <tr>
                  <td style="background:linear-gradient(135deg,#ef0000,#7f0d12); padding:32px; text-align:center;">
                    <div style="display:inline-block; background:#ef0000; color:#fff; font-size:28px; font-weight:900; padding:16px 18px; border-radius:18px;">
                      RC
                    </div>
                    <h1 style="margin:20px 0 0; font-size:34px; font-weight:900;">
                      Welcome to Sanity RC
                    </h1>
                    <p style="margin:10px 0 0; color:#fee2e2; font-size:16px;">
                      Your Rust Console panel license is ready.
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding:32px;">
                    <h2 style="margin:0; font-size:24px;">Thank you for your purchase.</h2>
                    <p style="color:#9ca3af; line-height:1.6; font-size:16px;">
                      Use the license key below to activate your Sanity RC account.
                    </p>

                    <div style="margin:26px 0; padding:20px; background:#080A0F; border:1px solid #374151; border-radius:16px; text-align:center;">
                      <p style="margin:0 0 8px; color:#9ca3af; font-size:13px; text-transform:uppercase; letter-spacing:1px;">
                        License Key
                      </p>
                      <div style="font-size:24px; color:#f87171; font-weight:900; letter-spacing:1px;">
                        {license_key}
                      </div>
                    </div>

                    <div style="text-align:center; margin:30px 0;">
                      <a href="{activation_link}"
                         style="background:#ef0000; color:white; text-decoration:none; padding:16px 28px; border-radius:14px; font-weight:900; display:inline-block;">
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

    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
      smtp.starttls()
      smtp.login(SMTP_USER, SMTP_PASSWORD)
      smtp.send_message(msg)

    print(f"LICENSE EMAIL SENT TO: {to_email}")
    return True