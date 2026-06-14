"""
Job Notifier — checks 500+ companies via ATS APIs + scraping
Sends email on new fresher/SDE/ML openings
"""

import os
import json
import hashlib
import smtplib
import requests
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# ─── CONFIG ────────────────────────────────────────────────────────────────────
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]      # your Gmail
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]   # Gmail App Password
RECEIVER_EMAIL  = os.environ["RECEIVER_EMAIL"]    # where to receive alerts (can be same)

SEEN_FILE = "data/seen_jobs.json"

KEYWORDS = [
    "software engineer", "sde", "software developer", "backend engineer",
    "data scientist", "ml engineer", "machine learning", "ai engineer",
    "platform engineer", "site reliability", "sre", "devops",
    "full stack", "fullstack", "associate engineer", "graduate engineer",
    "fresher", "fresh graduate", "entry level", "new grad", "campus hire",
    "data analyst", "data engineer", "analyst", "associate", "intern", "internship", "remote",
    "golang", "go"
]

EXCLUDE_KEYWORDS = [
    "senior", "staff", "principal", "director", "manager", "head of",
    "lead", "vp ", "vice president", "10+", "8+ years", "7+ years",
    "6+ years", "5+ years",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

# ─── ATS: GREENHOUSE ───────────────────────────────────────────────────────────
# Format: (Company Name, greenhouse_board_token)
GREENHOUSE_COMPANIES = [
    # FAANG-adjacent / Big Tech
    ("Stripe",          "stripe"),
    ("Databricks",      "databricks"),
    ("Cloudflare",      "cloudflare"),
    ("Atlassian",       "atlassian"),
    ("Figma",           "figma"),
    ("Notion",          "notion"),
    ("Airtable",        "airtable"),
    ("Brex",            "brex"),
    ("Robinhood",       "robinhood"),
    ("Plaid",           "plaid"),
    ("Coinbase",        "coinbase"),
    ("OpenAI",          "openai"),
    ("Anthropic",       "anthropic"),
    ("Scale AI",        "scaleai"),
    ("Hugging Face",    "huggingface"),
    ("Cohere",          "cohere"),
    ("Weights & Biases","wandb"),
    ("Palo Alto Networks","paloaltonetworks"),
    ("CrowdStrike",     "crowdstrike"),
    ("Rubrik",          "rubrik"),
    ("Cohesity",        "cohesity"),
    ("Pure Storage",    "purestorage"),
    ("Nutanix",         "nutanix"),
    ("Akamai",          "akamai"),
    ("HashiCorp",       "hashicorp"),
    ("PlanetScale",     "planetscale"),
    ("Grafana Labs",    "grafanalabs"),
    ("Datadog",         "datadog"),
    ("Zendesk",         "zendesk"),
    ("Twilio",          "twilio"),
    ("SendGrid",        "sendgrid"),
    ("Asana",           "asana"),
    ("Monday.com",      "mondaycom"),
    ("HubSpot",         "hubspot"),
    ("Intercom",        "intercom"),
    ("Amplitude",       "amplitude"),
    ("Mixpanel",        "mixpanel"),
    ("Segment",         "segment"),
    ("Contentful",      "contentful"),
    ("Zapier",          "zapier"),
    ("Linear",          "linear"),
    ("Vercel",          "vercel"),
    ("Netlify",         "netlify"),
    ("Retool",          "retool"),
    ("Postman",         "postman"),
    ("BrowserStack",    "browserstack"),
    ("Freshworks",      "freshworks"),
    ("Chargebee",       "chargebee"),
    ("Clevertap",       "clevertap"),
    ("MoEngage",        "moengage"),
    ("Nykaa",           "nykaa"),
    ("Razorpay",        "razorpay"),
    ("Zerodha",         "zerodha"),
    ("Groww",           "groww"),
    ("Slice",           "sliceit"),
    ("Jupiter",         "jupitermoney"),
    ("Smallcase",       "smallcase"),
    ("Darwinbox",       "darwinbox"),
    ("Leadsquared",     "leadsquared"),
    ("Hasura",          "hasura"),
    ("Setu",            "setu"),
    ("DeHaat",          "dehaat"),
    ("Meesho",          "meesho"),
    ("ShareChat",       "sharechat"),
    ("Dream11",         "dream11"),
    ("MPL",             "mpl"),
    ("Glance",          "glance"),
    ("InMobi",          "inmobi"),
    ("Dunzo",           "dunzo"),
    ("Zetwerk",         "zetwerk"),
    ("Delhivery",       "delhivery"),
    ("Shiprocket",      "shiprocket"),
    ("Licious",         "licious"),
    ("Country Delight", "countrydelight"),
    ("Ninjacart",       "ninjacart"),
    ("Udaan",           "udaan"),
    ("Porter",          "porter"),
    ("Rapido",          "rapido"),
    ("BlackBuck",       "blackbuck"),
    ("Ola Electric",    "olaelectric"),
    ("Ather Energy",    "atherenergy"),
    ("Simple Energy",   "simpleenergy"),
    ("upGrad",          "upgrad"),
    ("Unacademy",       "unacademy"),
    ("BYJU'S",          "byjus"),
    ("Vedantu",         "vedantu"),
    ("PhysicsWallah",   "physicswallah"),
    ("Eruditus",        "eruditus"),
    ("Springboard",     "springboard"),
    ("Scaler",          "scaler"),
    ("Stashfin",        "stashfin"),
    ("KreditBee",       "kreditbee"),
    ("MoneyTap",        "moneytap"),
    ("Axio",            "axio"),
    ("Progcap",         "progcap"),
    ("Lendingkart",     "lendingkart"),
    ("NoBroker",        "nobroker"),
    ("Housing.com",     "housing"),
    ("PropTiger",       "proptiger"),
    ("Magicbricks",     "magicbricks"),
    ("1mg",             "1mg"),
    ("Practo",          "practo"),
    ("Pristyn Care",    "pristyncare"),
    ("Cure.fit",        "curefit"),
    ("HealthifyMe",     "healthifyme"),
    ("Mfine",           "mfine"),
    ("Innovaccer",      "innovaccer"),
    ("Kinnate",         "kinnate"),
    ("Arcesium",        "arcesium"),
    ("Niyo",            "niyo"),
    ("Cashfree",        "cashfree"),
    ("Pagarbook",       "pagarbook"),
    ("OkCredit",        "okcredit"),
    ("Khatabook",       "khatabook"),
    ("BharatPe",        "bharatpe"),
    ("PayU",            "payu"),
    ("Juspay",          "juspay"),
    ("Perfios",         "perfios"),
    ("Finbox",          "finbox"),
    ("Lendbox",         "lendbox"),
    ("Recko",           "recko"),
    # Global SaaS / Remote-friendly
    ("GitLab",          "gitlab"),
    ("Fly.io",          "flyio"),
    ("Temporal",        "temporal"),
    ("Buf",             "buf"),
    ("Planetscale",     "planetscale"),
    ("Railway",         "railway"),
    ("Render",          "render"),
    ("Supabase",        "supabase"),
    ("Neon",            "neondatabase"),
    ("TigerBeetle",     "tigerbeetle"),
    ("ClickHouse",      "clickhouse"),
    ("Turso",           "turso"),
]

# ─── ATS: LEVER ───────────────────────────────────────────────────────────────
# Format: (Company Name, lever_company_slug)
LEVER_COMPANIES = [
    ("Uber",            "uber"),
    ("Lyft",            "lyft"),
    ("Airbnb",          "airbnb"),
    ("Dropbox",         "dropbox"),
    ("Pinterest",       "pinterest"),
    ("Reddit",          "reddit"),
    ("Discord",         "discord"),
    ("Canva",           "canva"),
    ("Miro",            "miro"),
    ("Loom",            "loom"),
    ("Coda",            "coda"),
    ("Linear",          "linear"),
    ("Sourcegraph",     "sourcegraph"),
    ("Descript",        "descript"),
    ("Pitch",           "pitchdeck"),
    ("Benchling",       "benchling"),
    ("Samsara",         "samsara"),
    ("Navan",           "navan"),
    ("Rippling",        "rippling"),
    ("Lattice",         "lattice"),
    ("Culture Amp",     "cultureamp"),
    ("15Five",          "15five"),
    ("Leapsome",        "leapsome"),
    ("Personio",        "personio"),
    ("Deel",            "deel"),
    ("Remote",          "remote"),
    ("Papaya Global",   "papayaglobal"),
    ("Oyster",          "oysterhr"),
    ("Multiverse",      "multiverse"),
    ("Synthesia",       "synthesia"),
    ("ElevenLabs",      "elevenlabs"),
    ("Mistral AI",      "mistralai"),
    ("Together AI",     "togetherai"),
    ("Anyscale",        "anyscale"),
    ("Modal",           "modal"),
    ("Replicate",       "replicate"),
    ("Runway",          "runwayml"),
    ("Ideogram",        "ideogram"),
    ("Perplexity",      "perplexityai"),
    ("Character.AI",    "characterai"),
    ("Inflection",      "inflection"),
    ("Adept",           "adept"),
    ("Imbue",           "imbue"),
    ("Jasper",          "jasperai"),
    ("Writer",          "writer"),
    ("Glean",           "glean"),
    ("Moveworks",       "moveworks"),
    ("Observe.AI",      "observeai"),
    ("Cresta",          "cresta"),
    ("Uniphore",        "uniphore"),
    ("Sprinklr",        "sprinklr"),
    ("Mediaocean",      "mediaocean"),
    ("IronNet",         "ironnet"),
    ("Lacework",        "lacework"),
    ("Orca Security",   "orcasecurity"),
    ("Wiz",             "wiz"),
    ("Snyk",            "snyk"),
    ("Socket",          "socket"),
    ("Semgrep",         "semgrep"),
    ("Endor Labs",      "endorlabs"),
    ("Chainguard",      "chainguard"),
    ("Teleport",        "teleport"),
    ("Cyera",           "cyera"),
    ("Torq",            "torq"),
    ("Drata",           "drata"),
    ("Vanta",           "vanta"),
    ("Secureframe",     "secureframe"),
    ("Tugboat Logic",   "tugboatlogic"),
    ("Incident.io",     "incidentio"),
    ("FireHydrant",     "firehydrant"),
    ("Blameless",       "blameless"),
    ("Rootly",          "rootly"),
    ("PagerDuty",       "pagerduty"),
    ("OpsGenie",        "opsgenie"),
    ("Chronosphere",    "chronosphere"),
    ("Lightstep",       "lightstep"),
    ("Honeycomb",       "honeycomb"),
    ("Cribl",           "cribl"),
    ("Mezmo",           "mezmo"),
    ("GreptimeDB",      "greptimedb"),
    ("VictoriaMetrics", "victoriametrics"),
    ("CRED",            "cred"),
    ("PhonePe",         "phonepe"),
    ("Zepto",           "zepto"),
    ("Swiggy",          "swiggy"),
    ("Zomato",          "zomato"),
    ("BigBasket",       "bigbasket"),
    ("Blinkit",         "blinkit"),
    ("MakeMyTrip",      "makemytrip"),
    ("Ola",             "ola"),
    ("Paytm",           "paytm"),
    ("BharatPe",        "bharatpe"),
    ("Fi Money",        "fimoney"),
]

# ─── ATS: ASHBY ───────────────────────────────────────────────────────────────
ASHBY_COMPANIES = [
    ("Resend",          "resend"),
    ("Neon DB",         "neon"),
    ("Turso",           "turso"),
    ("Zed",             "zed"),
    ("Warp",            "warp"),
    ("Arc Browser",     "thebrowser"),
    ("Codeium",         "codeium"),
    ("Cursor",          "anysphere"),
    ("Devin AI",        "cognition"),
    ("Mutable AI",      "mutableai"),
    ("Sweep",           "sweep"),
    ("Aider",           "aider"),
    ("Continue",        "continuedev"),
    ("Phind",           "phind"),
    ("You.com",         "youcom"),
    ("Pika",            "pika"),
    ("Udio",            "udio"),
    ("Suno",            "suno"),
    ("Luma AI",         "lumalabs"),
    ("Pika Labs",       "pikalabs"),
    ("Dify",            "dify"),
    ("LangChain",       "langchain"),
    ("LlamaIndex",      "llamaindex"),
    ("Vapi",            "vapi"),
    ("Bland AI",        "blandai"),
    ("Retell AI",       "retellai"),
    ("Cartesia",        "cartesia"),
    ("Deepgram",        "deepgram"),
    ("AssemblyAI",      "assemblyai"),
    ("Roboflow",        "roboflow"),
    ("Encord",          "encord"),
    ("Scale AI",        "scale"),
    ("Labelbox",        "labelbox"),
    ("Snorkel AI",      "snorkel"),
    ("Kili Tech",       "kili"),
]

# ─── DIRECT SCRAPE ────────────────────────────────────────────────────────────
# Companies that use custom career pages
# Format: (Company Name, careers_url, optional_job_list_selector)
SCRAPE_COMPANIES = [
    # FAANG
    ("Google",          "https://careers.google.com/jobs/results/?q=software+engineer&employment_type=FULL_TIME&degree=BACHELOR&jlo=en_US", None),
    ("Microsoft",       "https://jobs.microsoft.com/us/en/search#q=software+engineer&l=en_uSA&exp=Entry+Level", None),
    ("Amazon",          "https://www.amazon.jobs/en/search?base_query=software+engineer&loc_query=India&job_type=full-time&category=software-development", None),
    ("Meta",            "https://www.metacareers.com/jobs?offices[0]=India&teams[0]=Software+Engineering&experience_levels[0]=new+grad%2Fentry+level", None),
    ("Apple",           "https://jobs.apple.com/en-us/search?team=software-and-services-SFTWR&location=india-IND", None),
    # Indian IT Services
    ("TCS",             "https://ibegin.tcs.com/iBegin/", None),
    ("Infosys",         "https://career.infosys.com/joblist", None),
    ("Wipro",           "https://careers.wipro.com/careers-home/jobs?stretch=10&stretchUnit=KILOMETERS&location=India&woe=12&page=1", None),
    ("Cognizant",       "https://careers.cognizant.com/global/en/search-results?keywords=fresher", None),
    ("Accenture",       "https://www.accenture.com/in-en/careers/jobsearch?jk=fresher+software+engineer&vw=1", None),
    ("HCL Tech",        "https://www.hcltech.com/careers/jobs-search?keyword=fresher", None),
    ("Tech Mahindra",   "https://careers.techmahindra.com/search/?q=fresher+engineer", None),
    ("LTIMindtree",     "https://www.ltimindtree.com/careers/job-listings/?keyword=fresher", None),
    ("Persistent",      "https://www.persistent.com/careers/job-openings/?keyword=engineer", None),
    ("Mphasis",         "https://careers.mphasis.com/job-search-results/?keyword=fresher", None),
    ("Coforge",         "https://www.coforge.com/careers/job-listings?q=software+engineer", None),
    ("Capgemini",       "https://www.capgemini.com/in-en/careers/find-a-job/?search=fresher+engineer", None),
    ("Hexaware",        "https://hexaware.com/careers/?search=engineer", None),
    ("DXC Technology",  "https://careers.dxc.com/global/en/search-results?keywords=fresher+engineer+india", None),
    ("IBM India",       "https://www.ibm.com/in-en/employment/", None),
    ("Birlasoft",       "https://www.birlasoft.com/careers/current-openings?q=fresher", None),
    ("Cyient",          "https://careers.cyient.com/jobs?search=software+engineer", None),
    ("L&T Tech",        "https://careers.ltts.com/job-openings/", None),
    ("NTT Data",        "https://careers.nttdata.com/us/en/search-results?keywords=fresher+india", None),
    ("Genpact",         "https://jobs.genpact.com/listjobs/al/search/fresher", None),
    ("WNS",             "https://www.wns.com/careers/job-search?q=fresher", None),
    ("EXL Service",     "https://careers.exlservice.com/global/en/search-results?keywords=fresher+engineer", None),
    ("Nagarro",         "https://www.nagarro.com/en/careers/job-openings?keyword=engineer", None),
    # Banking / Finance
    ("Goldman Sachs",   "https://higher.gs.com/roles?query=software+engineer+india+entry+level", None),
    ("JP Morgan",       "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/requisitions?keyword=software+engineer+india", None),
    ("Morgan Stanley",  "https://morganstanley.tal.net/vx/brand-0/candidate/so/pm/1/pl/1/opp/all-opportunities/en-GB", None),
    ("Deutsche Bank",   "https://careers.db.com/professionals/search-roles/#/professional/keyword=software+engineer+india", None),
    ("Barclays",        "https://search.jobs.barclays/en_GB/careers/JobDetail/fresher+india", None),
    ("Citi India",      "https://jobs.citi.com/job/bangalore/software-engineer", None),
    ("HSBC",            "https://mycareer.hsbc.com/en_GB/external/SearchJobs/software+engineer?1_116_3=1601", None),
    ("BNY Mellon",      "https://bnymellon.eightfold.ai/careers?query=software+engineer+india", None),
    ("American Express","https://aexp.eightfold.ai/careers?query=engineer+india", None),
    ("Mastercard",      "https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers?q=software+engineer+india", None),
    ("Visa",            "https://corporate.visa.com/en/jobs/?q=software+engineer+india&categories=Technology", None),
    ("PayPal",          "https://paypal.eightfold.ai/careers?query=software+engineer+india", None),
    # Quant
    ("DE Shaw India",   "https://www.deshawindia.com/technical-positions.shtml", None),
    ("Graviton",        "https://gravitonresearch.com/careers", None),
    ("Tower Research",  "https://www.tower-research.com/open-positions", None),
    ("WorldQuant",      "https://www.worldquant.com/career-listing/", None),
    ("Optiver",         "https://optiver.com/working-at-optiver/career-opportunities/?field_category_value=All&field_location_value=APAC", None),
    ("Alphagrep",       "https://www.alphagrep.com/careers.html", None),
    # GCCs
    ("SAP Labs",        "https://jobs.sap.com/search/?q=software+engineer+india+entry+level", None),
    ("Oracle India",    "https://careers.oracle.com/jobs/#en/sites/jobsearch/jobs?keyword=software+engineer+india+junior", None),
    ("Samsung R&D",     "https://samsung.com/in/aboutsamsung/careers/", None),
    ("Walmart GTC",     "https://careers.walmart.com/results?q=software+engineer+india+fresher", None),
    ("Target India",    "https://india.target.com/careers/job-list", None),
    ("Honeywell",       "https://careers.honeywell.com/us/en/search-results?keywords=software+engineer+india+entry", None),
    ("Bosch",           "https://www.bosch-softwaretechnologies.com/en/careers/jobs/", None),
    ("Siemens India",   "https://new.siemens.com/in/en/company/jobs/search-careers.html?search=software+engineer", None),
    ("Dell India",      "https://jobs.dell.com/search-jobs/software+engineer+fresher/India/375", None),
    ("HP India",        "https://jobs.hp.com/en-us/search-jobs/software+engineer+india/", None),
    ("Intel India",     "https://jobs.intel.com/en/search#q=software%20engineer&t=Jobs&location=India", None),
    ("Cisco India",     "https://jobs.cisco.com/jobs/SearchJobs/software%20engineer?21178=%5B169482%5D&21178_format=6020&listFilterMode=1&21180=%5B78%5D&21180_format=6022", None),
    ("Qualcomm India",  "https://qualcomm.wd5.myworkdayjobs.com/External/jobs?q=software+engineer+india", None),
    ("Juniper Networks","https://jobs.juniper.net/careers?q=software+engineer+india+fresher", None),
    ("Palo Alto",       "https://jobs.paloaltonetworks.com/en/jobs/?search=software+engineer+india+fresher", None),
    ("Nutanix",         "https://jobs.nutanix.com/search/?q=software+engineer+india+fresher", None),
    ("NetApp",          "https://careers.netapp.com/jobs/?search=software+engineer+india", None),
    ("Fortinet",        "https://www.fortinet.com/corporate/careers/search-jobs.html#q=software+engineer+india", None),
    # Consulting
    ("Deloitte India",  "https://apply.deloitte.com/careers/SearchJobs/fresher+engineer?3_78_3=India", None),
    ("EY India",        "https://eygbl.referrals.selectminds.com/external-careers/jobs/search/fresher+technology+india", None),
    ("PwC India",       "https://www.pwc.in/careers/students/job-search.html", None),
    ("KPMG India",      "https://kpmg.com/in/en/home/careers/student-opportunities.html", None),
    ("ZS Associates",   "https://www.zs.com/careers/find-a-job?query=fresher+india", None),
    # Naukri-indexed companies (check Naukri directly for these)
    ("Myntra",          "https://careers.myntra.com/", None),
    ("Delhivery",       "https://www.delhivery.com/careers", None),
    ("MakeMyTrip",      "https://careers.makemytrip.com/Jobs", None),
    ("Ola",             "https://ola.com/careers", None),
    ("Fi Money",        "https://fi.money/careers", None),
    ("KreditBee",       "https://www.kreditbee.in/careers", None),
    ("Porter",          "https://porter.in/careers", None),
    ("Rapido",          "https://rapido.bike/careers", None),
    ("Cashfree",        "https://www.cashfree.com/careers", None),
    ("Juspay",          "https://juspay.in/careers", None),
    ("Perfios",         "https://www.perfios.com/careers", None),
    ("Innovaccer",      "https://innovaccer.com/company/careers", None),
    ("Practo",          "https://practo.com/company/careers", None),
    ("Khatabook",       "https://khatabook.com/careers/", None),
    ("NoBroker",        "https://www.nobroker.in/info/career/", None),
    ("Sprinklr",        "https://www.sprinklr.com/careers/", None),
    ("CleverTap",       "https://clevertap.com/company/careers/", None),
    ("MoEngage",        "https://www.moengage.com/company/careers/", None),
    ("Unacademy",       "https://unacademy.com/jobs", None),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    os.makedirs("data", exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def job_id(company: str, title: str, url: str) -> str:
    return hashlib.md5(f"{company}|{title}|{url}".encode()).hexdigest()

def is_relevant(title: str) -> bool:
    t = title.lower()
    if any(ex in t for ex in EXCLUDE_KEYWORDS):
        return False
    return any(kw in t for kw in KEYWORDS)

def send_email(jobs: list):
    if not jobs:
        return

    rows = ""
    for j in jobs:
        rows += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #eee;font-weight:bold;color:#1a1a2e">{j['company']}</td>
            <td style="padding:10px;border-bottom:1px solid #eee;">{j['title']}</td>
            <td style="padding:10px;border-bottom:1px solid #eee;">{j.get('location','India')}</td>
            <td style="padding:10px;border-bottom:1px solid #eee;"><a href="{j['url']}" style="background:#4f46e5;color:white;padding:6px 14px;border-radius:4px;text-decoration:none;font-size:13px">Apply</a></td>
        </tr>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:900px;margin:auto;padding:20px">
        <h2 style="color:#1a1a2e">🚀 {len(jobs)} New Job Alert(s) — {datetime.now().strftime('%d %b %Y, %I:%M %p')}</h2>
        <p style="color:#555">New fresher/SDE/ML openings found across your tracked companies.</p>
        <table style="width:100%;border-collapse:collapse;font-size:14px">
            <thead>
                <tr style="background:#1a1a2e;color:white">
                    <th style="padding:12px;text-align:left">Company</th>
                    <th style="padding:12px;text-align:left">Role</th>
                    <th style="padding:12px;text-align:left">Location</th>
                    <th style="padding:12px;text-align:left">Link</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="color:#aaa;font-size:12px;margin-top:30px">Sent by your Job Notifier bot — running on GitHub Actions</p>
    </body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 {len(jobs)} New Job Alert(s) — {datetime.now().strftime('%d %b')}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(SENDER_EMAIL, SENDER_PASSWORD)
        s.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

    print(f"✅ Email sent with {len(jobs)} jobs")

# ─── FETCHERS ─────────────────────────────────────────────────────────────────

def fetch_greenhouse(company: str, token: str) -> list:
    jobs = []
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []
        for job in r.json().get("jobs", []):
            title    = job.get("title", "")
            location = job.get("location", {}).get("name", "")
            apply    = job.get("absolute_url", "")
            if is_relevant(title):
                jobs.append({"company": company, "title": title, "location": location, "url": apply})
    except Exception as e:
        print(f"Greenhouse error [{company}]: {e}")
    return jobs

def fetch_lever(company: str, slug: str) -> list:
    jobs = []
    try:
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return []
        for job in r.json():
            title    = job.get("text", "")
            location = job.get("categories", {}).get("location", "")
            apply    = job.get("hostedUrl", "")
            if is_relevant(title):
                jobs.append({"company": company, "title": title, "location": location, "url": apply})
    except Exception as e:
        print(f"Lever error [{company}]: {e}")
    return jobs

def fetch_ashby(company: str, slug: str) -> list:
    jobs = []
    try:
        url = f"https://jobs.ashbyhq.com/api/non-user-facing/job-board/get-all-job-postings?organizationHostedJobsPageName={slug}"
        r = requests.get(url, timeout=15, headers=HEADERS)
        if r.status_code != 200:
            return []
        data = r.json()
        for job in data.get("jobPostings", []):
            title    = job.get("title", "")
            location = job.get("locationName", "")
            jid      = job.get("id", "")
            apply    = f"https://jobs.ashbyhq.com/{slug}/{jid}"
            if is_relevant(title):
                jobs.append({"company": company, "title": title, "location": location, "url": apply})
    except Exception as e:
        print(f"Ashby error [{company}]: {e}")
    return jobs

def fetch_scrape(company: str, url: str, selector) -> list:
    jobs = []
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        # Generic: find all links/text that look like job titles
        candidates = soup.find_all(["a", "h2", "h3", "h4", "li", "span", "div"],
                                   class_=lambda c: c and any(x in c.lower() for x in
                                   ["job", "role", "position", "title", "opening", "career"]))
        seen_titles = set()
        for el in candidates:
            title = el.get_text(strip=True)
            href  = el.get("href", url)
            if len(title) < 5 or len(title) > 120:
                continue
            if title in seen_titles:
                continue
            if is_relevant(title):
                seen_titles.add(title)
                full_url = href if href.startswith("http") else f"https://{url.split('/')[2]}{href}"
                jobs.append({"company": company, "title": title, "location": "India", "url": full_url})
    except Exception as e:
        print(f"Scrape error [{company}]: {e}")
    return jobs

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print(f"🔍 Job Notifier started at {datetime.now()}")
    seen   = load_seen()
    new_jobs = []

    # Greenhouse
    print(f"Checking {len(GREENHOUSE_COMPANIES)} Greenhouse companies...")
    for company, token in GREENHOUSE_COMPANIES:
        for job in fetch_greenhouse(company, token):
            jid = job_id(job["company"], job["title"], job["url"])
            if jid not in seen:
                seen.add(jid)
                new_jobs.append(job)
        time.sleep(0.3)

    # Lever
    print(f"Checking {len(LEVER_COMPANIES)} Lever companies...")
    for company, slug in LEVER_COMPANIES:
        for job in fetch_lever(company, slug):
            jid = job_id(job["company"], job["title"], job["url"])
            if jid not in seen:
                seen.add(jid)
                new_jobs.append(job)
        time.sleep(0.3)

    # Ashby
    print(f"Checking {len(ASHBY_COMPANIES)} Ashby companies...")
    for company, slug in ASHBY_COMPANIES:
        for job in fetch_ashby(company, slug):
            jid = job_id(job["company"], job["title"], job["url"])
            if jid not in seen:
                seen.add(jid)
                new_jobs.append(job)
        time.sleep(0.3)

    # Direct Scrape
    print(f"Checking {len(SCRAPE_COMPANIES)} direct scrape companies...")
    for company, url, selector in SCRAPE_COMPANIES:
        for job in fetch_scrape(company, url, selector):
            jid = job_id(job["company"], job["title"], job["url"])
            if jid not in seen:
                seen.add(jid)
                new_jobs.append(job)
        time.sleep(1)

    save_seen(seen)
    print(f"\n✅ Found {len(new_jobs)} new jobs")

    if new_jobs:
        send_email(new_jobs)
    else:
        print("No new jobs — no email sent")

if __name__ == "__main__":
    main()
