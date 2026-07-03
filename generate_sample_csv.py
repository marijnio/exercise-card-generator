import pandas as pd

# Define the full set of 12 exercises requested by the user, including details, print names, IDs, and common mistakes to avoid
data = [
    {
        "ID": "1",
        "Exercise_Name": "Glute Bridge March",
        "Print_Name": "Glute Bridge March",
        "Description": "Een uitstekende oefening voor het trainen van de billen, hamstrings en rompstabiliteit. Door om en om een leg te heffen, daag je de rotatiestabiliteit van je heupen en core extra uit.",
        "Form_Instruction_1": "Lieg plat op je rug met gebogen knieën en voeten plat op de grond op heupbreedte.",
        "Form_Instruction_2": "Span je billen aan en duw je heupen omhoog till je lichaam een rechte lijn vormt van schouders tot knieën.",
        "Form_Instruction_3": "Houd je heupen stabiel en til om en om een knie omhoog richting je borst in een marcherende beweging.",
        "Form_Instruction_4": "Zet je voet gecontroleerd terug en herhaal met het andere been, houd je heupen hoog.",
        "Avoid_Mistake": "Laat je heupen niet naar de grond zakken of zijwaarts kantelen als je één been optilt.",
        "Video_URL": "",
        "Primary_Muscles": "Billen, Hamstrings",
        "Secondary_Muscles": "Core, Onderrug"
    },
    {
        "ID": "2",
        "Exercise_Name": "Air Squat",
        "Print_Name": "Air Squat",
        "Description": "Het fundamentele kniebuigpatroon met lichaamsgewicht, ontworpen om uithoudingsvermogen van het onderlichaam, heupmobiliteit en rompstabiliteit op te bouwen.",
        "Form_Instruction_1": "Sta met je voeten iets breder dan schouderbreedte, tenen licht naar buiten gedraaid.",
        "Form_Instruction_2": "Houd je borst op en span je core aan, breng je heupen naar achteren alsof je op een stoel gaat zitten.",
        "Form_Instruction_3": "Duw je knieën naar buiten en laat je heupen zakken tot je dijen parallel zijn aan de vloer.",
        "Form_Instruction_4": "Duw krachtig door je hielen om terug te keren naar de startpositie.",
        "Avoid_Mistake": "Laat je knieën niet naar binnen vallen en voorkom dat je hakken van de vloer loskomen.",
        "Video_URL": "",
        "Primary_Muscles": "Quadriceps, Billen",
        "Secondary_Muscles": "Hamstrings, Kuiten, Core"
    },
    {
        "ID": "3",
        "Exercise_Name": "Goblet Squat",
        "Print_Name": "Goblet Squat",
        "Description": "Een essentiële oefening voor het onderlichaam die zich richt op de quadriceps, billen en core. Het gewicht aan de voorkant vasthouden verbetert de houding en zorgt voor een grotere squatdiepte.",
        "Form_Instruction_1": "Houd de kettlebell dicht bij je borst vast aan de handvatten, met je ellebogen omlaag gericht.",
        "Form_Instruction_2": "Sta met je voeten op schouderbreedte, tenen licht naar buiten en span je core aan.",
        "Form_Instruction_3": "Breng je heupen naar achteren en buig je knieën om te squatten, terwijl je de knieën naar buiten duwt.",
        "Form_Instruction_4": "Zak tot je dijen parallel zijn aan de vloer, duw dan door je hielen om op te staan.",
        "Avoid_Mistake": "Laat de kettlebell je bovenlichaam niet naar voren trekken; houd je borst op.",
        "Video_URL": "https://www.youtube.com/watch?v=M8H8HwVn-w0",
        "Primary_Muscles": "Quadriceps, Billen",
        "Secondary_Muscles": "Hamstrings, Core, Kuiten"
    },
    {
        "ID": "4",
        "Exercise_Name": "Floor Press",
        "Print_Name": "Floor Press",
        "Description": "Een borstpress uitgevoerd vanaf de grond, wat de bewegingsuitslag beperkt om de nadruk te leggen op de borst, voorste schouders en triceps terwijl de schouders worden ontzien.",
        "Form_Instruction_1": "Lieg plat op je rug op de grond, knieën gebogen, voeten plat, met een kettlebell in één hand.",
        "Form_Instruction_2": "Breng de kettlebell in de rackpositie met je elleboog op de grond in een hoek van 45 graden.",
        "Form_Instruction_3": "Duw de kettlebell verticaal omhoog richting het plafond tot je arm volledig gestrekt is.",
        "Form_Instruction_4": "Laat het gewicht gecontroleerd zakken tot je bovenarm weer zachtjes de vloer raakt.",
        "Avoid_Mistake": "Laat je elleboog niet hard op de grond klappen; controleer de excentrische fase.",
        "Video_URL": "",
        "Primary_Muscles": "Borst, Triceps",
        "Secondary_Muscles": "Schouders, Core"
    },
    {
        "ID": "5",
        "Exercise_Name": "Straight Leg Deadlift",
        "Print_Name": "Deadlift met gestrekte benen",
        "Description": "Een heupscharnierbeweging gericht op de achterste keten, specifiek om de hamstrings, billen en onderrug te rekken en te versterken.",
        "Form_Instruction_1": "Sta met voeten op heupbreedte en houd de kettlebell voor je dijen vast.",
        "Form_Instruction_2": "Houd je rug plat en je knieën licht gebogen, buig voorover vanuit je heupen om het gewicht te laten zakken.",
        "Form_Instruction_3": "Duw je heupen naar achteren en laat de kettlebell dicht langs je benen glijden.",
        "Form_Instruction_4": "Knijp in je billen en breng je heupen weer naar voren om rechtop te gaan staan.",
        "Avoid_Mistake": "Voorkom dat je rug bol trekt; houd de ruggengraat neutraal en scharnier vanuit de heupen.",
        "Video_URL": "",
        "Primary_Muscles": "Hamstrings, Billen, Onderrug",
        "Secondary_Muscles": "Bovenrug, Core"
    },
    {
        "ID": "6",
        "Exercise_Name": "Single Arm Bent Over Row",
        "Print_Name": "Single Arm Bent Over Row",
        "Description": "Een eenzijdige trekbeweging voor het bovenlichaam om rugkracht, lat-ontwikkeling en rompstabiliteit op te bouwen.",
        "Form_Instruction_1": "Neem een uitvalspas met één voet naar achteren, houd je rug plat en buig voorover vanuit de heupen.",
        "Form_Instruction_2": "Ondersteun je bovenlichaam door je niet-werkende onderarm op je voorste dij te laten rusten.",
        "Form_Instruction_3": "Houd de kettlebell in je werkende hand en trek je elleboog omhoog richting je ribbenkast.",
        "Form_Instruction_4": "Laat het gewicht gecontroleerd zakken tot je arm weer volledig gestrekt is.",
        "Avoid_Mistake": "Draai je schouders en torso niet open bij het omhoog trekken van het gewicht.",
        "Video_URL": "",
        "Primary_Muscles": "Lats, Rhomboïden, Biceps",
        "Secondary_Muscles": "Bovenrug, Core"
    },
    {
        "ID": "7",
        "Exercise_Name": "Side Lunge",
        "Print_Name": "Zijwaartse Lunge",
        "Description": "Een zijwaartse beweging gericht op kracht in één een been, heupmobiliteit en flexibiliteit van de binnenkant van de dijen.",
        "Form_Instruction_1": "Sta rechtop en houd de kettlebell voor je borst vast aan de handvatten.",
        "Form_Instruction_2": "Zet een grote stap opzij met één leg, waarbij je tenen naar voren blijven wijzen.",
        "Form_Instruction_3": "Duw je heupen naar achteren en buig je werkende knie, terwijl je het andere been volledig strekt.",
        "Form_Instruction_4": "Zet krachtig af met het gebogen been om terug te keren naar de startpositie.",
        "Avoid_Mistake": "Laat de knie van het gebogen been niet voorbij je tenen schieten of naar binnen knikken.",
        "Video_URL": "",
        "Primary_Muscles": "Quadriceps, Billen, Adductoren",
        "Secondary_Muscles": "Hamstrings, Core"
    },
    {
        "ID": "8",
        "Exercise_Name": "Hardstyle Plank",
        "Print_Name": "Hardstyle Plank",
        "Description": "Een intensieve variant van de standaard plank die is ontworpen om maximale spanning in de core, schouderstabiliteit en algehele lichaamsstijfheid te genereren.",
        "Form_Instruction_1": "Plaats je onderarmen en tenen op de grond, met je lichaam in een strakke rechte lijn.",
        "Form_Instruction_2": "Trek je ellebogen denkbeeldig naar je tenen en knijp je billen, quads and vuisten zo hard mogelijk samen.",
        "Form_Instruction_3": "Houd je nek lang, kijk naar de grond en adem oppervlakkig door de spanning heen.",
        "Form_Instruction_4": "Houd deze maximale spanning gedurende de hele set vast.",
        "Avoid_Mistake": "Laat je heupen niet doorhangen of juist te ver omhoog steken; behoud een planklijn.",
        "Video_URL": "",
        "Primary_Muscles": "Core, Schouders",
        "Secondary_Muscles": "Billen, Bovenrug"
    },
    {
        "ID": "9",
        "Exercise_Name": "Farmer's Carry",
        "Print_Name": "Farmer's Carry",
        "Description": "Een eenvoudige maar krachtige functionele oefening die gripkracht, schouderstabiliteit, lichaamshouding en core-uithoudingsvermogen opbouwt.",
        "Form_Instruction_1": "Til twee zware kettlebells veilig van de grond met een correcte deadlift-techniek.",
        "Form_Instruction_2": "Sta rechtop met je schouders naar achteren en beneden, borst op, en knijp stevig in de handvatten.",
        "Form_Instruction_3": "Loop vooruit met rustige, gecomputerd stappen terwijl je je lichaam perfect recht houdt.",
        "Form_Instruction_4": "Behoud een actieve houding en voorkom dat de gewichten gaan schommelen.",
        "Avoid_Mistake": "Voorkom dat je met je schouders gaan hangen of naar voren leunt; loop met een trotse houding.",
        "Video_URL": "",
        "Primary_Muscles": "Gripkracht, Core, Traps",
        "Secondary_Muscles": "Onderarmen, Bovenrug, Benen"
    },
    {
        "ID": "10",
        "Exercise_Name": "Deficit Push-up",
        "Print_Name": "Deficit Push-up",
        "Description": "Een push-up variant waarbij de kettlebell-handvatten worden gebruikt om de handen te verhogen, wat zorgt voor een grotere bewegingsuitslag en diepere stretch in de borst.",
        "Form_Instruction_1": "Plaats twee kettlebells met de platte kant op de grond op schouderbreedte en pak de handvatten vast.",
        "Form_Instruction_2": "Neem een sterke plankpositie aan, waarbij je hoofd, heupen en hielen op één lijn liggen.",
        "Form_Instruction_3": "Laat je borst zakken till tussen de kettlebell-handvatten, houd je onderarmen verticaal.",
        "Form_Instruction_4": "Duw jezelf krachtig omhoog tot de armen gestrekt zijn, houd je core constant aangespannen.",
        "Avoid_Mistake": "Laat je heupen of onderrug niet doorzakken tijdens het zakken; houd je core strak.",
        "Video_URL": "",
        "Primary_Muscles": "Borst, Triceps, Schouders",
        "Secondary_Muscles": "Core, Serratus Anterior"
    },
    {
        "ID": "11",
        "Exercise_Name": "Kettlebell Swing",
        "Print_Name": "Kettlebell Swing",
        "Description": "De basis van kettlebell training. Deze explosieve heupscharnierbeweging bouwt krachtige billen, hamstrings en core-kracht op, terwijl het je conditie verbetert.",
        "Form_Instruction_1": "Sta met je voeten iets breder dan schouderbreedte, buig vanuit je heupen en pak de kettlebell met twee handen vast.",
        "Form_Instruction_2": "Hike de kettlebell krachtig naar achteren tussen je benen, met een rechte rug en aangespannen schouders.",
        "Form_Instruction_3": "Strek je heupen explosief, knijp in je billen en swing de kettlebell tot schouderhoogte.",
        "Form_Instruction_4": "Laat de kettlebell door de zwaartekracht terugvallen en scharnier direct weer vanuit je heupen.",
        "Avoid_Mistake": "Maak er geen squat van; het is een heupscharnierbeweging waarbij je heupen naar achteren bewegen, niet omlaag.",
        "Video_URL": "https://www.youtube.com/watch?v=YSyGqiG4U40",
        "Primary_Muscles": "Hamstrings, Billen",
        "Secondary_Muscles": "Core, Onderrug, Grip"
    },
    {
        "ID": "12",
        "Exercise_Name": "Suitcase Deadlift",
        "Print_Name": "Suitcase Deadlift",
        "Description": "Een variant van de deadlift waarbij je het gewicht aan één kant vasthoudt. Dit daagt je zijdelingse rompstabiliteit en gripkracht maximaal uit.",
        "Form_Instruction_1": "Sta rechtop met je voeten op heupbreedte en plaats de kettlebell aan de buitenkant van één voet.",
        "Form_Instruction_2": "Scharnier vanuit je heupen en buig je knieën om het handvat van de kettlebell met één hand vast te pakken.",
        "Form_Instruction_3": "Houd je schouders perfect horizontaal en span je core aan om te voorkomen dat je lichaam zijwaarts kantelt.",
        "Form_Instruction_4": "Duw door je hielen om rechtop te gaan staan, knijp je billen samen, en laat het gewicht gecontroleerd zakken.",
        "Avoid_Mistake": "Voorkom dat je torso zijwaarts kantelt; houd je schouders en heupen gedurende de hele beweging recht.",
        "Video_URL": "https://www.youtube.com/watch?v=S6V_Z2V9-Z8",
        "Primary_Muscles": "Hamstrings, Billen, Core (Schuine buikspieren)",
        "Secondary_Muscles": "Gripkracht, Onderrug, Quadriceps"
    }
]

def main():
    df = pd.DataFrame(data)
    df.to_csv("workout_data.csv", index=False)
    print("Successfully generated workout_data.csv with all 12 exercises and common mistakes.")

if __name__ == "__main__":
    main()
