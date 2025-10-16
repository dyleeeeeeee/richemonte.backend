"""
Professional email templates for Concierge Bank 2FA system
Following the established design system for consistent branding
"""

import os


def base_email_template(
    title: str,
    hero_title: str,
    hero_subtitle: str,
    content_html: str,
    cta_text: str = None,
    cta_url: str = None,
    footer_text: str = None
) -> str:
    """Base email template following Concierge Bank design system"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')
    unsubscribe_url = f"{app_url}/unsubscribe"
    privacy_url = f"{app_url}/privacy"
    browser_url = f"{app_url}/email-preview"

    cta_section = ""
    if cta_text and cta_url:
        cta_section = f"""
                    <!-- CTA Section -->
                    <tr>
                        <td class="cta-section">
                            <a href="{cta_url}" class="cta-button">{cta_text}</a>
                        </td>
                    </tr>"""

    footer_content = footer_text or """
                            This is an automated security notification from Concierge Bank.<br>
                            If you did not request this action, please contact support immediately."""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{title} - Concierge Bank</title>
    <link href="https://fonts.googleapis.com/css2?family=Gruppo&family=Work+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!--[if mso]>
    <style type="text/css">
        table {{border-collapse: collapse; border-spacing: 0; border: 0;}}
    </style>
    <![endif]-->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            margin: 0 !important;
            padding: 0 !important;
            font-family: 'Work Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #FEFDFB !important;
            width: 100% !important;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table {{
            border-spacing: 0 !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            margin: 0 auto !important;
        }}
        td {{
            padding: 0;
            vertical-align: top;
        }}
        img {{
            border: 0;
            display: block;
            max-width: 100%;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }}
        a {{
            text-decoration: none;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: #FEFDFB;
            width: 100%;
        }}

        /* Header with Logo */
        .header-section {{
            background: linear-gradient(135deg, #FEFDFB 0%, #FAF9F7 100%);
            padding: 30px 40px;
            text-align: center;
            border-bottom: 3px solid #F2CA27;
        }}
        .header-section img {{
            max-width: 300px;
            width: 100%;
            height: auto;
            margin: 0 auto;
        }}

        /* Hero Section */
        .hero-section {{
            background: linear-gradient(135deg, #F2CA27 0%, #EBA420 100%);
            padding: 50px 40px;
            text-align: center;
        }}
        .hero-title {{
            font-family: 'Gruppo', sans-serif;
            font-size: 36px;
            font-weight: 400;
            color: #1a1a1a;
            text-align: center;
            margin: 0 0 15px 0;
            letter-spacing: 1px;
        }}
        .hero-subtitle {{
            font-family: 'Work Sans', sans-serif;
            font-size: 18px;
            color: #1a1a1a;
            margin: 0;
            opacity: 0.9;
        }}

        /* Content Section */
        .content-section {{
            padding: 50px 40px;
            background: #FEFDFB;
            color: #1a1a1a;
            line-height: 1.8;
        }}
        .content-title {{
            font-family: 'Gruppo', sans-serif;
            font-size: 28px;
            color: #1a1a1a;
            margin: 0 0 20px 0;
            letter-spacing: 1px;
        }}
        .content-text {{
            font-family: 'Work Sans', sans-serif;
            font-size: 16px;
            color: #404040;
            margin: 0 0 20px 0;
            line-height: 1.8;
        }}

        /* CTA Button */
        .cta-section {{
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #FAF9F7 0%, #F5F3F0 100%);
        }}
        .cta-button {{
            display: inline-block;
            padding: 16px 48px;
            background: linear-gradient(135deg, #F2CA27 0%, #EBA420 100%);
            color: #1a1a1a;
            font-family: 'Work Sans', sans-serif;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(242, 202, 39, 0.3);
            letter-spacing: 0.5px;
        }}
        .cta-button:hover {{
            background: linear-gradient(135deg, #EBA420 0%, #D08C1D 100%);
            box-shadow: 0 6px 16px rgba(242, 202, 39, 0.4);
            transform: translateY(-2px);
        }}

        /* Security Notice Box */
        .security-notice {{
            background: linear-gradient(135deg, #FEFDFB 0%, #FAF9F7 100%);
            border: 2px solid #F2CA27;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}
        .security-title {{
            font-family: 'Work Sans', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 15px 0;
        }}
        .security-code {{
            font-family: 'Courier New', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #F2CA27;
            background: #1a1a1a;
            padding: 15px 30px;
            border-radius: 6px;
            display: inline-block;
            margin: 15px 0;
            letter-spacing: 4px;
        }}

        /* Backup Codes Box */
        .backup-codes {{
            background: #FAF9F7;
            border: 1px solid #E8E6E3;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }}
        .backup-title {{
            font-family: 'Work Sans', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 15px 0;
        }}
        .codes-grid {{
            display: table;
            width: 100%;
            border-collapse: collapse;
        }}
        .code-item {{
            display: table-cell;
            padding: 8px 12px;
            background: #FEFDFB;
            border: 1px solid #E8E6E3;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #1a1a1a;
            font-weight: 600;
        }}

        /* Info Box */
        .info-box {{
            background: #F5F3F0;
            border-left: 4px solid #F2CA27;
            padding: 20px;
            margin: 25px 0;
        }}
        .info-title {{
            font-family: 'Work Sans', sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 10px 0;
        }}
        .info-text {{
            font-family: 'Work Sans', sans-serif;
            font-size: 14px;
            color: #525252;
            margin: 0;
            line-height: 1.6;
        }}

        /* Divider */
        .divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #F2CA27 50%, transparent 100%);
            margin: 40px 0;
        }}

        /* Footer Section */
        .footer-section {{
            background: #1a1a1a;
            padding: 40px 40px 30px 40px;
            text-align: center;
            color: #FAF9F7;
            font-size: 14px;
            line-height: 1.6;
        }}
        .footer-section img {{
            max-width: 200px;
            width: 100%;
            height: auto;
            margin: 0 auto 20px auto;
            opacity: 0.9;
        }}
        .footer-text {{
            font-family: 'Work Sans', sans-serif;
            margin: 10px 0;
            color: #E8E6E3;
        }}
        .footer-links {{
            margin: 20px 0 10px 0;
        }}
        .footer-links a {{
            color: #F2CA27;
            text-decoration: none;
            margin: 0 10px;
            font-weight: 500;
        }}
        .footer-links a:hover {{
            color: #FFD54F;
            text-decoration: underline;
        }}
        .footer-address {{
            font-family: 'Work Sans', sans-serif;
            font-size: 12px;
            color: #a3a3a3;
            margin: 15px 0 0 0;
            font-style: normal;
        }}

        /* Responsive Design */
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
            }}
            .header-section {{
                padding: 25px 20px !important;
            }}
            .header-section img {{
                max-width: 250px !important;
            }}
            .hero-section {{
                padding: 40px 20px !important;
            }}
            .hero-title {{
                font-size: 28px !important;
            }}
            .hero-subtitle {{
                font-size: 16px !important;
            }}
            .content-section {{
                padding: 40px 25px !important;
            }}
            .content-title {{
                font-size: 24px !important;
            }}
            .content-text {{
                font-size: 15px !important;
            }}
            .security-code {{
                font-size: 24px !important;
                padding: 12px 20px !important;
            }}
            .codes-grid {{
                display: block !important;
            }}
            .code-item {{
                display: inline-block !important;
                width: 45% !important;
                margin: 2px !important;
                font-size: 12px !important;
                padding: 6px 8px !important;
            }}
            .cta-section {{
                padding: 30px 20px !important;
            }}
            .cta-button {{
                padding: 14px 36px !important;
                font-size: 15px !important;
            }}
            .footer-section {{
                padding: 30px 20px 25px 20px !important;
            }}
            .footer-section img {{
                max-width: 180px !important;
            }}
        }}

        @media only screen and (max-width: 480px) {{
            .hero-title {{
                font-size: 24px !important;
            }}
            .content-title {{
                font-size: 22px !important;
            }}
            .security-code {{
                font-size: 20px !important;
                padding: 10px 15px !important;
                letter-spacing: 2px !important;
            }}
            .code-item {{
                width: 100% !important;
                font-size: 11px !important;
            }}
            .cta-button {{
                padding: 12px 32px !important;
                font-size: 14px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #FEFDFB;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #FEFDFB;">
        <tr>
            <td align="center" style="padding: 0;">
                <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">

                    <!-- Header with Logo -->
                    <tr>
                        <td class="header-section">
                            <img src="https://conciergebank.us/_next/image?url=%2Flogos%2Fbanner.png&w=3840&q=75" alt="Concierge Bank" style="max-width: 300px; height: auto; margin: 0 auto;">
                        </td>
                    </tr>

                    <!-- Hero Section -->
                    <tr>
                        <td class="hero-section">
                            <h1 class="hero-title">{hero_title}</h1>
                            <p class="hero-subtitle">{hero_subtitle}</p>
                        </td>
                    </tr>

                    <!-- Content Section -->
                    <tr>
                        <td class="content-section">
                            {content_html}
                        </td>
                    </tr>{cta_section}

                    <!-- Footer Section -->
                    <tr>
                        <td class="footer-section">
                            <img src="https://conciergebank.us/_next/image?url=%2Flogos%2Fbanner.png&w=3840&q=75" alt="Concierge Bank" style="max-width: 200px; height: auto; margin: 0 auto 20px auto; opacity: 0.9;">
                            <p class="footer-text">{footer_content}</p>

                            <div class="footer-links">
                                <a href="{unsubscribe_url}">Unsubscribe</a> |
                                <a href="{browser_url}">View in Browser</a> |
                                <a href="{privacy_url}">Privacy Policy</a>
                            </div>

                            <p class="footer-address">
                                © 2025 Concierge Bank. All rights reserved.<br>
                                Member FDIC | Equal Housing Lender
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def twofa_setup_email(full_name: str, backup_codes: list) -> str:
    """Professional 2FA setup confirmation email with backup codes"""

    # Format backup codes in a grid
    codes_html = ""
    for i in range(0, len(backup_codes), 4):
        codes_html += '<tr>'
        for j in range(4):
            if i + j < len(backup_codes):
                codes_html += f'<td class="code-item">{backup_codes[i + j]}</td>'
            else:
                codes_html += '<td class="code-item">&nbsp;</td>'
        codes_html += '</tr>'

    content_html = f"""
                            <h3 class="content-title">Dear {full_name or 'Valued Client'},</h3>

                            <p class="content-text">
                                Two-Factor Authentication has been successfully enabled for your Concierge Bank account.
                                You will now receive a verification code via email each time you log in.
                            </p>

                            <div class="backup-codes">
                                <h4 class="backup-title">⚠️ Important: Save Your Backup Codes</h4>
                                <p class="content-text" style="margin-bottom: 20px;">
                                    Store these backup codes in a safe place. You can use them to access your account if you lose access to your email:
                                </p>
                                <table class="codes-grid" cellpadding="0" cellspacing="0" border="0">
                                    {codes_html}
                                </table>
                                <p class="info-text" style="margin-top: 15px; font-style: italic;">
                                    Each code can only be used once. Generate new codes if you use them all.
                                </p>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">📧 How It Works</h4>
                                <ul class="info-text" style="padding-left: 20px; list-style-type: disc;">
                                    <li>When you log in, you'll receive a 6-digit code via email</li>
                                    <li>Enter the code within 10 minutes to complete login</li>
                                    <li>If you can't access your email, use a backup code</li>
                                    <li>You can disable 2FA anytime in Security Settings</li>
                                </ul>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="2FA Setup Complete",
        hero_title="🔐 Two-Factor Authentication Enabled",
        hero_subtitle="Your account is now more secure",
        content_html=content_html,
        cta_text="Manage Security Settings",
        cta_url=f"{app_url}/dashboard/settings/security",
        footer_text="This is an automated security notification from Concierge Bank. If you did not enable 2FA, please contact support immediately."
    )


def twofa_code_email(full_name: str, otp_code: str) -> str:
    """Professional 2FA OTP verification email"""

    content_html = f"""
                            <h3 class="content-title">Dear {full_name or 'Valued Client'},</h3>

                            <p class="content-text">
                                To complete your login to Concierge Bank, please enter the verification code below:
                            </p>

                            <div class="security-notice">
                                <h4 class="security-title">Your Verification Code</h4>
                                <div class="security-code">{otp_code}</div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">⏰ Code Expiration</h4>
                                <p class="info-text">
                                    This code will expire in <strong>10 minutes</strong>. For security reasons, each code can only be used once.
                                </p>
                            </div>

                            <div class="info-box" style="background: #F0F9F0; border-left-color: #10B981;">
                                <h4 class="info-title" style="color: #065F46;">🛡️ Security Notice</h4>
                                <ul class="info-text" style="color: #065F46; padding-left: 20px; list-style-type: disc;">
                                    <li>Never share this code with anyone</li>
                                    <li>If you didn't request this login, contact support immediately</li>
                                    <li>Use backup codes if you can't access this email</li>
                                </ul>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Login Verification",
        hero_title="🔐 Login Verification Required",
        hero_subtitle="Please verify your identity",
        content_html=content_html,
        cta_text="Return to Login",
        cta_url=f"{app_url}/login",
        footer_text="This code was requested for login to your Concierge Bank account. If you did not request this, please secure your account immediately."
    )
