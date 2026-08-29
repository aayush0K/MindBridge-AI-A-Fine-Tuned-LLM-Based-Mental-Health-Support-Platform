"""
Generate mental_health_corpus.json with 215+ curated QA pairs.
Run: python scripts/generate_corpus.py
"""

import json
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "corpus" / "mental_health_corpus.json"

CATEGORIES = {
    "anxiety": 35,
    "depression": 35,
    "stress": 25,
    "sleep": 20,
    "loneliness": 20,
    "self_esteem": 20,
    "grief": 15,
    "anger": 15,
    "relationships": 15,
    "crisis": 15,
}

TEMPLATES = {
    "anxiety": [
        ("I feel anxious all the time and can't relax", "Living with constant anxiety is genuinely exhausting, and your feelings are completely valid. Can you tell me what situations tend to make the anxiety feel strongest?"),
        ("My heart races before every exam and I can't focus", "Exam anxiety is so common, especially when you care about doing well. That physical rush is your body trying to protect you. What helps you feel even slightly calmer before tests?"),
        ("I worry about everything — my future, family, health", "When worry spreads into every area of life, it can feel impossible to catch a break. You're carrying a lot. Which worry has been loudest for you lately?"),
        ("Social situations make me panic and I avoid people", "Social anxiety can make connection feel terrifying instead of comforting. Avoidance often makes sense in the moment. What would feel like a small, safe step toward someone you trust?"),
        ("I had a panic attack and I'm scared it will happen again", "Panic attacks are frightening, and fear of another one is very real. You're not weak for feeling this way. After it passed, what helped your body settle even a little?"),
        ("I can't stop overthinking small things at night", "Nighttime overthinking steals rest and peace. Your mind is trying to solve problems, even when there's no solution at 2am. Would it help to name one thought you're stuck on?"),
        ("I feel on edge even when nothing bad is happening", "That constant edge can be exhausting — like waiting for something to go wrong. Your nervous system may be overstimulated. Have you noticed anything that briefly eases that tension?"),
        ("I'm anxious about my job interview tomorrow", "Interview nerves show you care about the opportunity. Many people rehearse, breathe, or visualize — what have you tried so far?"),
        ("My parents expect too much and I feel anxious about disappointing them", "Family pressure in Indian households can feel heavy. Wanting to honor your parents while staying true to yourself is a real tension. What would 'good enough' look like to you right now?"),
        ("I feel anxious in crowded places like the metro", "Crowds can overwhelm the senses and trigger fight-or-flight. You're not alone in this. Do you have a coping strategy that works even a little in those moments?"),
    ],
    "depression": [
        ("I have no motivation and feel empty inside", "That feeling of emptiness is one of the hardest things to carry. You're not broken. Have you been able to talk to anyone about how you've been feeling?"),
        ("I don't enjoy things I used to love", "Losing interest in things you once enjoyed is a painful sign something needs care. It doesn't mean those joys are gone forever. When did you last feel even a flicker of enjoyment?"),
        ("I feel hopeless about my future", "Hopelessness can make tomorrow feel pointless. I hear how heavy that is. Is there one small thing today that felt even slightly bearable?"),
        ("I sleep all day but still feel tired", "Depression often disrupts sleep in both directions — too much or too little. Your body may be asking for rest in the only way it knows. How long has this pattern been going on?"),
        ("I feel like a burden to my friends and family", "Feeling like a burden is a common thought with depression, but it doesn't reflect your worth. People who care about you often want to support you. Have you shared any of this with someone you trust?"),
        ("Academic pressure is making me feel depressed", "Academic stress in competitive environments can drain joy and energy. Your worth is not your grades. What part of school feels heaviest right now?"),
        ("I cry often without knowing why", "Unexplained tears can be your body's way of releasing what words can't hold. You don't need a reason for your feelings to matter. Would you like to explore what was happening before the tears?"),
        ("I feel numb and disconnected from everyone", "Numbness can be as painful as sadness — it's still suffering. Connection may feel far away right now. Is there anyone, even one person, you feel slightly safer around?"),
        ("I lost interest in eating and taking care of myself", "When basic self-care feels impossible, depression may be deep. You're not failing — you're struggling. Have you been able to eat or drink anything small today?"),
        ("Everything feels pointless and I question why I try", "Questioning effort when you're depleted is understandable. You don't have to solve life's meaning today. What's one tiny thing that used to give you a moment of peace?"),
    ],
    "stress": [
        ("Work deadlines are crushing me and I can't cope", "Deadline pressure can feel like drowning. Your stress is a signal that your load may be too heavy. Which deadline is weighing on you most?"),
        ("I'm stressed about money and supporting my family", "Financial stress affects the whole household and carries deep responsibility. You're carrying a lot. Have you been able to talk to anyone about practical next steps?"),
        ("Balancing college, internship, and family is overwhelming", "Wearing multiple roles at once is genuinely overwhelming. Something often has to give — and that's not failure. Which role feels most urgent this week?"),
        ("My boss is toxic and I'm stressed every Sunday night", "Sunday scaries tied to a difficult workplace are exhausting. Your reaction makes sense. What would feeling even slightly safer at work look like?"),
        ("I feel stressed but I don't know the exact cause", "Sometimes stress shows up before we can name it. Your body may be responding to accumulated pressure. What's changed in your life recently, even small things?"),
        ("Family arguments leave me stressed for days", "Family conflict can linger in your body long after the conversation ends. That residual stress is valid. Do you have space to decompress after those moments?"),
        ("I'm stressed about my board exam results", "Waiting for results can be agonizing — the uncertainty is its own kind of pain. Many students feel this. What helps you get through difficult waiting periods?"),
        ("Too many responsibilities — I can't say no to anyone", "Difficulty saying no often comes from wanting to be helpful or avoid conflict. Your limits matter too. What would you say no to if you felt you could?"),
        ("I'm stressed about moving to a new city for work", "Big transitions stir stress even when they're positive. Leaving familiar support takes courage. What part of the move worries you most?"),
        ("Constant notifications and hustle culture stress me out", "Always-on culture can keep your nervous system activated. It's okay to want boundaries. Have you tried any digital or schedule boundaries?"),
    ],
    "sleep": [
        ("I can't fall asleep no matter how tired I am", "Insomnia when you're exhausted is cruel. Your mind may be protecting you by staying alert. What tends to run through your head at bedtime?"),
        ("I wake up at 3am and can't go back to sleep", "Middle-of-the-night waking is common with stress and anxiety. You're not alone. What do you usually do when you're awake at that hour?"),
        ("I have nightmares about past events", "Nightmares can make sleep feel unsafe. Your mind may be processing trauma or stress. Have these been recent, and do you feel safe during the day?"),
        ("I sleep too much but never feel rested", "Oversleeping without rest often points to depression or burnout. Your body may need recovery, not just hours. How's your mood when you wake up?"),
        ("My sleep schedule is completely irregular", "Irregular sleep disrupts mood and energy. Small consistency can help over time. What time do you usually feel most naturally sleepy?"),
        ("I stay up scrolling because quiet feels uncomfortable", "Late-night scrolling often fills silence when feelings feel too big. That's a common coping pattern. What might feel gentler than the phone before bed?"),
        ("I'm exhausted from caring for a sick parent at night", "Caregiver fatigue is real and often invisible. You're giving a lot. Is there anyone who could share even one night of responsibility?"),
        ("Caffeine and stress are ruining my sleep", "Stress and stimulants can feed each other in a loop. Noticing the pattern is a good first step. When do you usually have your last coffee or tea?"),
        ("I dread going to bed because my thoughts get louder", "Bedtime can amplify worries when there's no distraction. A wind-down ritual sometimes helps. Have you tried journaling or breathing before sleep?"),
        ("Shift work is destroying my sleep and mood", "Shift work challenges your body's natural rhythm. That strain is legitimate. What small adjustment has helped even slightly?"),
    ],
    "loneliness": [
        ("I feel lonely even when I'm around people", "Loneliness in a crowd is painfully common — it's about connection quality, not headcount. What kind of connection do you wish you had?"),
        ("I moved away from home and feel isolated", "Moving away from familiar support is a major adjustment. Missing home doesn't mean you're failing. Who do you still feel connected to, even from a distance?"),
        ("No one really understands what I'm going through", "Feeling misunderstood can deepen loneliness. Your experience is valid even if others don't get it yet. Would talking to a counselor or support group feel possible?"),
        ("I lost touch with friends after graduation", "Life transitions often scatter friend groups. That loss hurts. Is there one person you'd consider reaching out to?"),
        ("I spend weekends alone and it hurts", "Empty weekends can amplify loneliness. You're not alone in feeling this. What would a comforting weekend look like, even in a small way?"),
        ("I feel like I don't belong anywhere", "Belonging is a deep human need. Feeling outside can be crushing. Where have you felt even slightly accepted before?"),
        ("Social media makes me feel more lonely", "Comparing curated lives to your own often deepens isolation. Your feelings make sense. What would taking a break from scrolling feel like?"),
        ("I'm introverted but I still crave connection", "Wanting connection while needing solitude isn't contradictory. Both can be true. What low-energy connection might feel doable?"),
        ("My roommate and I don't talk — I feel alone at home", "Home should feel safe; silence there can sting. Would a small gesture — tea, a note — feel possible to break the ice?"),
        ("I work from home and barely see anyone", "Remote work can shrink your social world quickly. Loneliness here is structural, not personal failing. What one social ritual could you add this week?"),
    ],
    "self_esteem": [
        ("I feel worthless compared to everyone on LinkedIn", "Comparison on professional platforms can shrink your sense of worth. Your path is yours alone. What achievement of yours gets overlooked when you scroll?"),
        ("I feel like an imposter at my new job", "Imposter feelings often visit capable people in new roles. Evidence of your skills may exist even if you dismiss it. What feedback have you received that you brushed off?"),
        ("I hate how I look and avoid mirrors", "Body image struggles are painful and common. You deserve kindness toward yourself. When did these feelings become strongest?"),
        ("I never feel good enough for my parents", "Seeking parental approval while building your own identity is hard. Your worth isn't only their approval. What would you say to a friend in your situation?"),
        ("I criticize myself constantly in my head", "That inner critic can be relentless. Noticing it is already a step toward change. What would you say if a friend spoke about themselves that way?"),
        ("I failed an exam and feel like a complete failure", "One exam measures performance in a moment, not your value as a person. Many successful people have failed tests. What would recovery look like step by step?"),
        ("Everyone seems more confident than me", "Confidence often looks louder than it feels inside. Many people mask insecurity. What would acting 'as if' look like in one small situation?"),
        ("I don't believe compliments people give me", "Dismissing praise often protects against disappointment but also blocks self-compassion. What if one compliment were partly true?"),
        ("I feel stupid when I speak up in meetings", "Speaking up takes courage; self-doubt afterward is common. Your voice matters. What would help you prepare for the next meeting?"),
        ("I've been rejected and my self-esteem crashed", "Rejection hurts deeply and can shake how you see yourself. The pain is real. What do you know to be true about yourself beyond this moment?"),
    ],
    "grief": [
        ("I lost my grandmother and can't stop grieving", "Losing someone who raised or loved you leaves a lasting ache. Grief has no timetable. What do you miss most about her?"),
        ("I feel guilty for laughing after someone died", "Guilt mixed with moments of joy is normal in grief. Laughing doesn't mean you love them less. How are you caring for yourself through this?"),
        ("I never got to say goodbye properly", "Unfinished goodbyes can haunt grief. Your longing to have said more is love speaking. Would writing a letter to them feel meaningful?"),
        ("Anniversaries of their death are especially hard", "Anniversary grief can feel as fresh as the first day. Planning gentle support for those dates can help. What would comfort you on that day?"),
        ("My family expects me to move on but I'm not ready", "Grief timelines differ; pressure to 'move on' can isolate you. Your pace is valid. What do you need from people around you?"),
        ("I lost a pet and people don't understand my pain", "Pet loss is real grief. Those bonds matter deeply. Tell me about them — what made your connection special?"),
        ("I'm grieving the end of a relationship", "Relationship loss is a form of grief — dreams and routines die too. Heartbreak is legitimate. What part of the loss hurts most right now?"),
        ("I feel angry at the world after my loss", "Anger is a common part of grief, not a character flaw. It often protects deeper sadness. What are you most angry about?"),
        ("I dream about the person I lost every night", "Grief dreams can feel like visits or reopening wounds. Both are normal. Do the dreams bring comfort or more pain?"),
        ("I moved on practically but emotionally I'm stuck", "Functioning while grieving inside is exhausting. You're allowed to still hurt. What feeling have you been pushing away?"),
    ],
    "anger": [
        ("I snap at people I love and regret it immediately", "Anger toward loved ones often comes from stress or hurt underneath. Regret shows you care. What usually triggers the snap?"),
        ("I feel rage I can't express safely", "Unexpressed anger can build pressure. Finding safe outlets matters. What happens to your body when rage rises?"),
        ("Traffic and daily irritations make me furious", "Daily friction can accumulate into disproportionate anger. Your nervous system may be overloaded. What else has been stressing you lately?"),
        ("I'm angry at myself for past mistakes", "Self-directed anger can be harsh and looping. You were doing your best with what you knew then. What would forgiveness look like in one small step?"),
        ("Injustice in the news makes me constantly angry", "Moral anger at injustice is human. It can also drain you. How do you balance caring with protecting your peace?"),
        ("I was yelled at growing up and now I struggle with anger", "Childhood exposure to anger shapes how we regulate it. Patterns can be unlearned with support. Have you considered talking to a therapist about this?"),
        ("I feel angry when I'm actually hurt or scared", "Anger often masks softer feelings like hurt or fear. Naming the primary emotion can help. Under the anger, what might you be feeling?"),
        ("My partner and I fight loudly and I hate it", "Conflict cycles can feel scary and shameful. Pausing before escalation is a skill you can build. What usually starts the fights?"),
        ("I punch walls when overwhelmed — I want to stop", "Physical anger outlets can feel urgent but risky. Wanting to stop is important. What warning signs appear in your body before you hit a wall?"),
        ("Passive aggression is ruining my friendships", "Indirect anger often protects against vulnerability but damages trust. Noticing the pattern is a start. What are you afraid would happen if you spoke directly?"),
    ],
    "relationships": [
        ("My partner and I keep having the same argument", "Repeating arguments often mean an underlying need isn't met. The topic may be a symptom. What do you each really need in those moments?"),
        ("I'm heartbroken after a breakup", "Breakups can feel like grief — because they are. Allow yourself time. What part of the relationship do you miss most?"),
        ("I don't trust my partner after they lied", "Broken trust is painful and takes time to rebuild, if you choose to. Your caution makes sense. What would rebuilding trust require from both of you?"),
        ("My parents don't approve of my relationship", "Family disapproval adds stress to love. Your feelings and their concerns both matter. What would a honest conversation look like?"),
        ("I feel neglected in my marriage", "Feeling unseen by a partner is lonely. Your need for attention is valid. Have you been able to name what neglect looks like for you?"),
        ("Friend drama is affecting my mental health", "Friendship conflict can destabilize your whole week. Boundaries may help. What outcome would feel fairest to you?"),
        ("I'm scared of being abandoned", "Abandonment fear often comes from past experiences. It can shape how you attach now. When do you notice this fear strongest?"),
        ("I can't set boundaries with toxic family", "Boundaries with family are among the hardest. Small limits still count. What's one boundary that would protect your peace?"),
        ("Long distance is straining our relationship", "Distance tests trust and communication. Strain doesn't mean failure. What helps you feel connected across the miles?"),
        ("I feel jealous and ashamed of it", "Jealousy often signals insecurity or unmet needs, not bad character. Shame makes it harder to address. What fear sits under the jealousy?"),
    ],
    "crisis": [
        ("I don't want to be here anymore", "CRISIS"),
        ("I've been thinking about hurting myself", "CRISIS"),
        ("Sometimes I think everyone would be better off without me", "CRISIS"),
        ("I have a plan to end my life", "CRISIS"),
        ("I can't go on like this anymore", "CRISIS"),
        ("I want to die and I mean it", "CRISIS"),
        ("I've been cutting myself to feel something", "CRISIS"),
        ("I took pills hoping I wouldn't wake up", "CRISIS"),
        ("There's no point in living anymore", "CRISIS"),
        ("I'm going to kill myself tonight", "CRISIS"),
    ],
}

EXTRA_BY_CATEGORY = {
    "anxiety": [
        ("My chest feels tight when I'm anxious", "Physical anxiety symptoms are real and frightening. Tight chest often comes with stress breathing. Have you tried slow exhale breathing?"),
        ("I avoid driving because of anxiety", "Driving anxiety can limit freedom significantly. Gradual exposure with support sometimes helps. What part of driving feels scariest?"),
        ("Health anxiety makes me google symptoms constantly", "Health anxiety feeds on uncertainty; googling often increases fear. You're trying to feel safe. What reassurance would actually help?"),
        ("I feel anxious about climate and the future of the world", "Eco-anxiety reflects care for the planet and future generations. Taking small actionable steps can restore agency. What one action feels meaningful to you?"),
        ("Presentation anxiety ruins my performance", "Performance anxiety is common; preparation plus grounding can help. What happens in your body right before you speak?"),
    ],
    "depression": [
        ("Seasonal changes make my depression worse", "Seasonal mood shifts are documented and valid. Light, routine, and support can help. Have you noticed a pattern across years?"),
        ("I feel guilty for being depressed when others have it worse", "Pain isn't a competition. Your suffering counts regardless of others' stories. What would self-compassion sound like today?"),
        ("Postpartum feelings are darker than I expected", "Perinatal mood struggles are common and treatable. You're not a bad parent for feeling this. Have you spoken to a healthcare provider?"),
        ("Medication for depression makes me nervous", "Questions about medication are important to explore with a doctor. Fear of side effects is understandable. What would you want to ask a psychiatrist?"),
        ("I smile in public but fall apart alone", "High-functioning depression is exhausting — holding it together costs energy. You're allowed to need help even if you seem fine outside."),
    ],
    "stress": [
        ("Caregiver burnout is destroying my mental health", "Caring for others while neglecting yourself depletes reserves. Burnout is not selfishness. What tiny respite could you schedule this week?"),
        ("Startup life stress is constant", "Entrepreneurial stress rarely has an off switch. Boundaries protect sustainability. What would a non-negotiable rest block look like?"),
        ("Wedding planning stress is overwhelming", "Big life events carry joy and pressure together. It's okay to ask for help delegating. What task could someone else take?"),
        ("I'm stressed about my visa and immigration status", "Immigration uncertainty is a profound stressor. Your fear is understandable. Do you have legal or community support available?"),
        ("Political news stress affects my daily mood", "Staying informed while protecting mental health is a balance many struggle with. Curating intake can help. What limit might feel right?"),
    ],
    "sleep": [
        ("Partner's snoring keeps me awake and irritable", "Sleep disruption affects mood and patience. Earplugs, separate sleep, or medical check may help. Have you been able to discuss it calmly?"),
        ("Jet lag messed up my sleep for weeks", "Travel across time zones disrupts circadian rhythm. Recovery takes patience. Are you back home now or still adjusting?"),
        ("I use alcohol to fall asleep but feel worse", "Alcohol may induce sleep but reduces quality. Wanting rest is valid; healthier tools exist. Would you consider talking to a doctor?"),
        ("Menopause hot flashes wake me every night", "Hormonal sleep disruption is real and tiring. Medical support can improve nights. Have you explored options with a clinician?"),
        ("Anxiety about tomorrow's meeting keeps me awake", "Anticipatory anxiety at night is common. Writing worries down or a brief plan sometimes eases the mind. What's the main fear about the meeting?"),
    ],
    "loneliness": [
        ("I'm the only one in my friend group without a partner", "Singlehood in coupled friend groups can feel isolating. Your timeline is your own. What connections nourish you outside romance?"),
        ("Chronic illness limits my social life", "Health barriers to socializing are real, not personal failure. Online or low-energy connection may help. What format feels most doable?"),
        ("I feel lonely in my marriage", "Loneliness within partnership hurts deeply. Naming it is brave. Have you been able to tell your partner what you need?"),
        ("Retirement left me without daily social contact", "Work often provides structure and connection; retirement shifts both. New routines take time. What activity might bring you near people?"),
        ("I'm shy and lonely but afraid of rejection", "Fear of rejection keeps many people isolated. Small steps reduce risk. What's the gentlest social step you could try?"),
    ],
    "self_esteem": [
        ("Therapy made me realize how harsh my inner voice is", "Noticing the inner critic is powerful — awareness precedes change. What would a kinder voice say about today?"),
        ("I compare my body to influencers daily", "Curated images distort reality. Your body deserves respect. What account or habit could you change first?"),
        ("I feel behind in life at 30", "Societal timelines are arbitrary; many paths unfold later. Your pace is valid. What would 'enough' mean for you this year?"),
        ("Public speaking terror hurts my career", "Speaking anxiety is treatable with practice and support. Many leaders still feel nerves. What small speaking practice could you try?"),
        ("I was bullied and still carry low self-worth", "Bullying wounds can last years; healing is possible with support. You deserved better then. What would you tell your younger self?"),
    ],
    "grief": [
        ("Miscarriage grief feels invisible to others", "Pregnancy loss grief is profound and often minimized. Your baby mattered. Have you found anyone who validates this loss?"),
        ("I lost my job and I'm grieving that identity", "Job loss is identity loss too. Mourning that is appropriate. What parts of yourself did that role hold?"),
        ("My sibling died and our family doesn't talk about it", "Silent grief in families can isolate survivors. Breaking silence takes courage. Would sharing a memory feel possible?"),
        ("I'm grieving my health after diagnosis", "Health grief is real — mourning the body or life you expected. Adjustment takes time. What support have you found?"),
        ("Holiday seasons without them are unbearable", "First holidays without someone are especially sharp. Planning rituals of remembrance may help. What tradition would honor them?"),
    ],
    "anger": [
        ("Road rage scares me — I want calmer reactions", "Recognizing dangerous anger patterns is important. Pause techniques and therapy can help. What happens in the seconds before you react?"),
        ("I'm angry at God or fate after tragedy", "Spiritual or existential anger is part of many grief journeys. Your questions are allowed. What would comfort look like if not answers?"),
        ("Workplace bullying makes me angry and helpless", "Bullying combines anger with powerlessness. Documenting and seeking HR or external support may help. Do you feel safe reporting?"),
        ("I dissociate when angry instead of expressing it", "Shutdown during anger is a protective response. Learning safe expression takes time. Do you notice body signals before shutdown?"),
        ("Hormonal changes make my anger unpredictable", "Hormonal mood shifts are physical, not character flaws. Tracking cycles and talking to a doctor can help. Have you discussed this with a clinician?"),
    ],
    "relationships": [
        ("We're considering couples therapy", "Choosing therapy together shows commitment to the relationship. That's a positive step. What issues do you most want to address?"),
        ("I love my friend but they crossed a boundary", "Boundary violations strain trust. Naming the hurt is valid. What would repair require from them?"),
        ("Cultural differences with in-laws cause tension", "Blending families across cultures takes negotiation. Your stress is understandable. What boundary would help most?"),
        ("I'm codependent and lose myself in relationships", "Codependency often comes from early patterns of caregiving. Recovery involves reclaiming self. What do you enjoy when you're alone?"),
        ("Online dating rejection is hurting my confidence", "Dating app rejection is high-volume and impersonal — it rarely reflects your worth. Taking breaks can restore perspective. How long have you been at it?"),
    ],
    "crisis": [
        ("I researched methods to end my life", "CRISIS"),
        ("Nobody would miss me if I were gone", "CRISIS"),
        ("I feel suicidal but I'm scared to tell anyone", "CRISIS"),
        ("Self-harm is the only way I cope with pain", "CRISIS"),
        ("I don't see any way out of this pain", "CRISIS"),
    ],
}


def build_corpus() -> list[dict]:
    entries: list[dict] = []
    counter = 1

    for category, target in CATEGORIES.items():
        pool = list(TEMPLATES.get(category, [])) + list(EXTRA_BY_CATEGORY.get(category, []))
        idx = 0
        while len([e for e in entries if e["category"] == category]) < target:
            ctx, resp = pool[idx % len(pool)]
            entry_id = f"{category[:3]}_{counter:03d}"
            if category == "crisis":
                entry_id = f"crisis_{counter:03d}"
            keywords = [w for w in ctx.lower().split() if len(w) > 4][:5]
            entries.append({
                "id": entry_id,
                "category": category if category != "sleep" else "sleep",
                "context": ctx,
                "response": resp,
                "keywords": keywords,
            })
            counter += 1
            idx += 1

    return entries


def main():
    corpus = build_corpus()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    counts: dict[str, int] = {}
    for e in corpus:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    print(f"Wrote {len(corpus)} entries to {OUTPUT}")
    for cat, n in sorted(counts.items()):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
