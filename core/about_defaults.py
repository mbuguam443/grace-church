"""Default content for the public About page.

Kept separate from models so both the model and its data migration can use the
same text without importing model classes.
"""

ABOUT_HISTORY_INTRO = (
    "Grace Church Munyaka testifies to God's grace, providence, and faithfulness. "
    "What began as God's quiet preparation in the life of one family has grown into a "
    "vibrant local church dedicated to proclaiming the Gospel of Jesus Christ."
)

ABOUT_HISTORY_BODY = "\n\n".join([
    "In 2023, God graciously provided for Harry and Alice and they purchased land in "
    "Zone-T, Ruiru East, Juja East, Kiambu County. They later acquired an adjoining plot, "
    "which Harry dedicated to the Lord as an offering of thanksgiving. That land would "
    "become the future home of Grace Church.",
    "After moving into their home in January 2025, Harry invited neighbours for what was "
    "meant to be a men's fellowship. Families came together instead, and it naturally "
    "became a weekly Friday family fellowship centered on prayer, fellowship, and Bible study.",
    "As the fellowship grew, there was a desire to have a new church within the community. "
    "After prayer and seeking another ministry to begin work in Zone-T, Harry became "
    "convinced that God was calling him to plant a church.",
    "On 22 June 2025, Harry and Alice met with Pastor Dr. Joseph Kinyanjui and his wife of "
    "FBMI Ruiru Church for prayer, counsel, and encouragement, marking the commissioning of "
    "the emerging ministry.",
    "The first official worship service was held on 29 June 2025. The inaugural sermon came "
    "from 2 Peter 3:18, and this verse inspired the name Grace Church.",
])

ABOUT_CALL = (
    "To grow in the grace and knowledge of our Lord and Savior Jesus Christ (2 Peter 3:16).\n\n"
    "We are committed to nurturing spiritual maturity through God's Word, prayer, worship, "
    "fellowship, and faithful service. As we grow in Christ, we seek to reflect His love, "
    "share His Gospel, and bring glory to His name in all that we do."
)

ABOUT_DIVINE_PROMISE = (
    "An open door (Revelation 3:8).\n\n"
    "This divine promise gives us confidence to proclaim the Gospel, serve our community, "
    "and fulfill the mission He has entrusted to us."
)

ABOUT_MILESTONES = "\n".join([
    "2023 | Land purchased and dedicated for future ministry.",
    "Jan 2025 | Weekly family fellowship began.",
    "22 Jun 2025 | Prayer and commissioning with FBMI Ruiru.",
    "29 Jun 2025 | First Grace Church worship service.",
    "28 Dec 2025 | First baptismal service held.",
    "27 Jul 2026 | Moved into the new church building and held the first Thanksgiving Service.",
    "2 Aug 2026 | Seventh baptized member recorded and Grace Church received official cover documents from FBMI Ruiru.",
])

FEATURED_EVENT_TITLE = "Annual Revival Crusade 2024"
FEATURED_EVENT_DESCRIPTION = (
    "Join us for our most anticipated event of the year! Five nights of powerful worship, "
    "anointed preaching, and life-changing miracles. Guest speaker: Bishop Michael Okonkwo. "
    "Expect transformation, healing, and a fresh touch from God."
)
FEATURED_EVENT_DATE = "Nov 11-15, 2024"
FEATURED_EVENT_TIME = "6:00 PM - 9:00 PM"
FEATURED_EVENT_VENUE = "Main Sanctuary"
FEATURED_EVENT_AUDIENCE = "Everyone"


def about_defaults():
    return {
        'about_history_intro': ABOUT_HISTORY_INTRO,
        'about_history_body': ABOUT_HISTORY_BODY,
        'about_call': ABOUT_CALL,
        'about_divine_promise': ABOUT_DIVINE_PROMISE,
        'about_milestones': ABOUT_MILESTONES,
        'featured_event_title': FEATURED_EVENT_TITLE,
        'featured_event_description': FEATURED_EVENT_DESCRIPTION,
        'featured_event_date': FEATURED_EVENT_DATE,
        'featured_event_time': FEATURED_EVENT_TIME,
        'featured_event_venue': FEATURED_EVENT_VENUE,
        'featured_event_audience': FEATURED_EVENT_AUDIENCE,
    }
