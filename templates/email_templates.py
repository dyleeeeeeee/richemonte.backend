"""
Professional email templates for Concierge Bank
Following the established design system for consistent branding and DRY principles
"""
from core.config import LUXURY_GOLD_COLOR
import os


def base_email_template(
    title: str,
    hero_title: str,
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
                            This is an automated notification from Concierge Bank.<br>
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

        /* Hero Image Section */
        .hero-image-section {{
            position: relative;
            overflow: hidden;
            background: #1a1a1a;
        }}
        .hero-image {{
            width: 100%;
            height: auto;
            display: block;
            opacity: 0.9;
        }}
        .hero-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(26, 26, 26, 0.3) 0%, rgba(26, 26, 26, 0.7) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 60px 40px;
        }}
        .hero-title {{
            font-family: 'Gruppo', sans-serif;
            font-size: 48px;
            font-weight: 400;
            color: #FEFDFB;
            text-align: center;
            margin: 0;
            line-height: 1.2;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            letter-spacing: 1px;
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

        /* Transaction Details */
        .transaction-details {{
            background: #FAF9F7;
            border: 1px solid #E8E6E3;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }}
        .transaction-title {{
            font-family: 'Work Sans', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0 0 15px 0;
        }}
        .transaction-item {{
            display: table;
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }}
        .transaction-label {{
            display: table-cell;
            padding: 8px 12px 8px 0;
            font-family: 'Work Sans', sans-serif;
            font-weight: 600;
            color: #1a1a1a;
            width: 40%;
            vertical-align: top;
        }}
        .transaction-value {{
            display: table-cell;
            padding: 8px 0;
            font-family: 'Work Sans', sans-serif;
            color: #525252;
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
            .hero-overlay {{
                padding: 40px 20px !important;
            }}
            .hero-title {{
                font-size: 32px !important;
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
            .transaction-item {{
                display: block !important;
            }}
            .transaction-label, .transaction-value {{
                display: block !important;
                width: 100% !important;
                padding: 4px 0 !important;
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
                font-size: 28px !important;
            }}
            .content-title {{
                font-size: 22px !important;
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

                    <!-- Hero Image Section -->
                    <tr>
                        <td class="hero-image-section" style="position: relative;">
                            <img src="https://www.richemont.com/media/vy0f4smm/richemont-hq-entrance-evening-_subpage.png" alt="Concierge Bank" class="hero-image" style="width: 600px; height: 400px; object-fit: cover;">
                            <div class="hero-overlay">
                                <h1 class="hero-title">{hero_title}</h1>
                            </div>
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


def welcome_email(full_name: str) -> str:
    """Professional welcome email for new Concierge Bank members"""

    content_html = f"""
                            <h3 class="content-title">Welcome to Excellence</h3>
                            <p class="content-text">
                                At Concierge Bank, we understand that your financial journey is unique. Our personalized banking solutions are designed to provide you with the exceptional service and expertise you deserve.
                            </p>
                            <p class="content-text">
                                Experience banking that adapts to your lifestyle, with dedicated advisors ready to help you achieve your financial goals.
                            </p>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Welcome to Concierge Bank",
        hero_title="Welcome to Excellence",
        hero_subtitle="",  # Not used in new template
        content_html=content_html,
        cta_text="Explore Our Services",
        cta_url=f"{app_url}",
        footer_text="Welcome to Concierge Bank! Your account is now active and ready for use."
    )


def account_created_email(account_type: str, account_number: str, initial_deposit: float) -> str:
    """Professional account creation confirmation email"""

    content_html = f"""
                            <h3 class="content-title">Account Successfully Created</h3>

                            <p class="content-text">
                                Congratulations! Your new {account_type} account has been successfully opened at Concierge Bank.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">📋 Account Details</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Account Type:</div>
                                    <div class="transaction-value">{account_type}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Account Number:</div>
                                    <div class="transaction-value">{account_number}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Initial Balance:</div>
                                    <div class="transaction-value">${initial_deposit:,.2f}</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">💳 What's Next</h4>
                                <ul class="info-text" style="padding-left: 20px; list-style-type: disc;">
                                    <li>Funds are available immediately for use</li>
                                    <li>Order checks and cards as needed</li>
                                    <li>Set up automatic transfers and bill payments</li>
                                    <li>Contact your relationship manager for personalized guidance</li>
                                </ul>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Account Created",
        hero_title="Account Opened Successfully",
        content_html=content_html,
        cta_text="View Account Details",
        cta_url=f"{app_url}/dashboard/accounts",
        footer_text="Your new account is active and ready for transactions."
    )


def card_approved_email(card_brand: str, card_type: str, card_last_four: str, credit_limit: float) -> str:
    """Professional card approval email"""

    content_html = f"""
                            <h3 class="content-title">Card Application Approved</h3>

                            <p class="content-text">
                                Congratulations! Your {card_brand} {card_type} card application has been approved.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">💳 Card Details</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Card Type:</div>
                                    <div class="transaction-value">{card_brand} {card_type}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Card Number:</div>
                                    <div class="transaction-value">•••• •••• •••• {card_last_four}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Credit Limit:</div>
                                    <div class="transaction-value">${credit_limit:,.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Delivery Time:</div>
                                    <div class="transaction-value">5-7 business days</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">🚀 Getting Started</h4>
                                <ul class="info-text" style="padding-left: 20px; list-style-type: disc;">
                                    <li>Your card will arrive via secure courier</li>
                                    <li>Activate your card when it arrives</li>
                                    <li>Set up online banking and mobile alerts</li>
                                    <li>Enjoy exclusive benefits and rewards</li>
                                </ul>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Card Approved",
        hero_title="Card Application Approved",
        content_html=content_html,
        cta_text="Manage Cards",
        cta_url=f"{app_url}/dashboard/cards",
        footer_text="Your new card is on its way! Track delivery status in your dashboard."
    )


def transfer_confirmation_email(amount: float, new_balance: float) -> str:
    """Professional transfer confirmation email"""

    content_html = f"""
                            <h3 class="content-title">Transfer Completed Successfully</h3>

                            <p class="content-text">
                                Your transfer has been processed successfully. The funds are now available in your account.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">💸 Transfer Summary</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Transfer Amount:</div>
                                    <div class="transaction-value">${amount:,.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">New Balance:</div>
                                    <div class="transaction-value">${new_balance:,.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Processing Time:</div>
                                    <div class="transaction-value">Instant</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">🔒 Security & Tracking</h4>
                                <p class="info-text">
                                    All transfers are secured with bank-level encryption. Track your transaction history
                                    and set up spending alerts in your dashboard for complete peace of mind.
                                </p>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Transfer Confirmation",
        hero_title="Transfer Completed",
        content_html=content_html,
        cta_text="View Transaction History",
        cta_url=f"{app_url}/dashboard/transactions",
        footer_text="Your transfer has been completed. Funds are available immediately."
    )


def bill_payment_email(payee_name: str, amount: float, payment_date: str) -> str:
    """Professional bill payment confirmation email"""

    content_html = f"""
                            <h3 class="content-title">Bill Payment Processed</h3>

                            <p class="content-text">
                                Your bill payment has been successfully processed. Thank you for choosing Concierge Bank for your payment needs.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">📄 Payment Details</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Payee:</div>
                                    <div class="transaction-value">{payee_name}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Amount Paid:</div>
                                    <div class="transaction-value">${amount:,.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Payment Date:</div>
                                    <div class="transaction-value">{payment_date}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Status:</div>
                                    <div class="transaction-value">Completed</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">💡 Payment Management</h4>
                                <p class="info-text">
                                    Set up automatic bill payments to never miss a due date. Manage all your recurring payments
                                    from your dashboard for complete convenience and peace of mind.
                                </p>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Bill Payment Confirmation",
        hero_title="Bill Payment Completed",
        content_html=content_html,
        cta_text="Manage Bill Payments",
        cta_url=f"{app_url}/dashboard/bills",
        footer_text="Your bill payment has been completed. Keep this confirmation for your records."
    )


def check_deposit_email(amount: float, check_number: str) -> str:
    """Professional check deposit confirmation email"""

    content_html = f"""
                            <h3 class="content-title">Check Deposit Received</h3>

                            <p class="content-text">
                                Your check deposit has been received and is being processed. Funds will be available according to our standard hold policy.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">📝 Deposit Details</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Deposit Amount:</div>
                                    <div class="transaction-value">${amount:,.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Check Number:</div>
                                    <div class="transaction-value">{check_number}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Processing Time:</div>
                                    <div class="transaction-value">1-5 business days</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Status:</div>
                                    <div class="transaction-value">In Processing</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">⏱️ Availability Timeline</h4>
                                <ul class="info-text" style="padding-left: 20px; list-style-type: disc;">
                                    <li>$0 - $200: Available immediately</li>
                                    <li>$201 - $5,000: Available in 1 business day</li>
                                    <li>Over $5,000: Available in 2-5 business days</li>
                                    <li>Large deposits may require additional verification</li>
                                </ul>
                            </div>

                            <div class="info-box" style="background: #FFF8E1; border-left-color: #F2CA27;">
                                <h4 class="info-title" style="color: #B8860B;">💡 Mobile Deposit Tip</h4>
                                <p class="info-text" style="color: #B8860B;">
                                    For faster processing, try our mobile check deposit feature available in the Concierge Bank app.
                                    Deposits made before 2 PM are typically processed the same business day.
                                </p>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Check Deposit Confirmation",
        hero_title="Check Deposit Received",
        content_html=content_html,
        cta_text="Track Deposit Status",
        cta_url=f"{app_url}/dashboard/deposits",
        footer_text="Your check deposit is being processed. Track the status in your dashboard."
    )


def check_order_email(design: str, quantity: int, price: float) -> str:
    """Professional check order confirmation email"""

    content_html = f"""
                            <h3 class="content-title">Check Order Confirmed</h3>

                            <p class="content-text">
                                Your premium check order has been received and is being processed by our artisan printers.
                            </p>

                            <div class="transaction-details">
                                <h4 class="transaction-title">📮 Order Details</h4>
                                <div class="transaction-item">
                                    <div class="transaction-label">Design:</div>
                                    <div class="transaction-value">{design}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Quantity:</div>
                                    <div class="transaction-value">{quantity} checks</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Total Price:</div>
                                    <div class="transaction-value">${price:.2f}</div>
                                </div>
                                <div class="transaction-item">
                                    <div class="transaction-label">Delivery Time:</div>
                                    <div class="transaction-value">7-10 business days</div>
                                </div>
                            </div>

                            <div class="info-box">
                                <h4 class="info-title">🎨 Premium Quality</h4>
                                <p class="info-text">
                                    Your checks are printed on premium security paper with advanced anti-fraud features.
                                    Each check includes microprinting, chemical protection, and UV security features.
                                </p>
                            </div>

                            <div class="info-box" style="background: #F0F9F0; border-left-color: #10B981;">
                                <h4 class="info-title" style="color: #065F46;">🚚 Shipping Information</h4>
                                <p class="info-text" style="color: #065F46;">
                                    Your checks will be shipped via secure courier with signature confirmation.
                                    You'll receive a tracking number via email once your order ships.
                                </p>
                            </div>"""

    app_url = os.environ.get('NEXT_PUBLIC_APP_URL', 'https://conciergebank.us')

    return base_email_template(
        title="Check Order Confirmation",
        hero_title="Check Order Received",
        content_html=content_html,
        cta_text="Reorder Checks",
        cta_url=f"{app_url}/dashboard/checks",
        footer_text="Your check order is being processed. You'll receive shipping updates via email."
    )
