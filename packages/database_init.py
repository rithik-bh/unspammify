club_descriptions = [
    ['Silhouette Club', 'Silhouette club is the creative society of the university, which aims to promote the rich and vibrant art by organizing activities like painting, sketching, calligraphy, decoration, craft work, graffiti and contemporary designing. The club hosts various exhibitions, workshops and competitions. It also organizes trips to art museums and encourages students to participate in college fests.'],
    ['MUN Society', 'The MUN society focuses on enhancing the student experience by providing a platform to improve skills like critical thinking, public speaking, group communication, & research and policy analysis. The society follows the United Nations core values of Integrity, Professionalism and Respect for Diversity, and aims to create leaders of tomorrow. Its activities include organizing and hosting workshops, debates and MUN conferences.'],
    ['Alexis Club', 'Alexis is not merely a club but an outlet and a platform for the students who want to work for the society and leave a mark. The club conducts activities to protect the nature and also provide students with opportunities to work for the welfare of the society. Alexis is involved in various initiatives like teaching the underprivileged, organizing visits to places like old age homes, an orphanage, yoga, meditation, tree plantation, etc.'],
    ['Robotics Club', 'The club helps the students to form a brief understanding of various concepts and dynamics of Robotics. Students of the Robotics Club attend workshops, hold competitions and take part in different events to strengthen their technical skills'],
    ['Pulse', "The basic idea behind this club is to promote healthy adventure activities like river rafting, trekking and camping. The club aims at familiarizing the students with the beauty and the thrill that’s hidden in nature. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."],
    ['Cerebrum Club', 'Cerebrum Club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.'],
    ['Flucs', "The basic idea behind this club is to promote healthy adventure activities like river rafting, trekking and camping. The club aims at familiarizing the students with the beauty and the thrill that’s hidden in nature. Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."],
    ['Spark Club',
        'SPARK is a student Club which closely works with the Centre for Innovation and Entrepreneurship (CIE) and the Bennett Hatchery to nurture creativity and an entrepreneurial bent of mind amongst students. Our objectives include: encouraging creative thinking, supporting future start upfounders, and facilitating interaction with entrepreneurs, industry expertsand venture capitalists.'],
    ['Nomads', 'Nomads club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.'],
    ['Spice Macay', 'This is the society for the promotion of Indian classical music and culture amongst youth. The university through this club organizes various cultural events to keep the students rooted to Indian culture and traditions.'],
    ['Virtuoso Club', 'This club is the spice of the University with its fathomless zest and exuberance towards dance, drama and music. The club sponsors the deserving students in big events and organizes activities to unearth the hidden talent.'],
    ['ISAAC Club', """
        The Photography Club is a platform built for photography Beginners, Amateurs, Enthusiasts and Hobbyists, on an idea to connect every photography enthusiast by a common thread. We are growing on a single set of mind where everyone is welcome to join us, and stimulate the inception of new ideas in this visual art. We are here in order to inculcate and motivate the art of photography in our students.
        We are a place where people are not judged by their skills, rather they have to come up with enthusiasm, and rest we help them in providing the right expertise. We are there to give the support to one other and learn from the unlearned skills from our team as well as build on each other's artistry. We seek to display our love of photography through the constructive criticism of our peers, leisure activities, and the promotion of photography throughout the campus and carve a niche for ourselves as a club on different platforms.
        We are an inclusive club, where we also promote creative videography. We welcome all sorts of individuals to come and join us over our monthly sessions, discuss their aspirations and creativity, find the like minded people and transform them through various club activities.
    """],
    ['Astronomy Club', 'Astronomy Club as the name suggests is a group of travel enthusiats and adventure sports lovers. The club aims to make students experience the beauty and the thrill that’s hidden in nature. The members participates in adventure activities like river rafting, trekking and camping.']
]


def getURLSyntax(str):
    # converting Silhouette Club to silhouette-club
    return str.strip().replace(" ", "-").lower()


def initializeDatabase(db_connection):
    database = db_connection[0]
    cursor = db_connection[1]

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS `users`
        (
            `FirstName` varchar(255) NOT NULL,
            `LastName` varchar(255) NOT NULL,
            `ID` varchar(255) NOT NULL UNIQUE,
            `Password` varchar(100) NOT NULL,
            `InterestedActivites` text
        );
    
    """)
    database.commit()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS `admins`
        (
            `URL_Name` varchar(255) NOT NULL,
            `Password` varchar(100) NOT NULL
        );
    
    """)
    database.commit()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS `club_events`
        (
            `EventID` varchar(255) NOT NULL PRIMARY KEY,
            `URL_Name` varchar(255) NOT NULL,
            `EventDate` varchar(255) NOT NULL,
            `EventTime` varchar(255) NOT NULL,
            `EventVenue` varchar(255) NOT NULL,
            `EventDescription` text NOT NULL
        );

    """)
    database.commit()

    cursor.execute("""

        DROP TABLE IF EXISTS `club_descriptions`
        CREATE TABLE IF NOT EXISTS `club_descriptions`
        (
            `Name` varchar(255) NOT NULL,
            `URL_Name` varchar(255) NOT NULL,
            `Description` varchar(255) NOT NULL
        );

    """)
    database.commit()

    # NOW ADD CLUB DESCRIPTIONS TO TABLE
    for club in club_descriptions:
        cursor.execute("INSERT INTO `club_descriptions` VALUES(%s,%s,%s)",
                       (club[0], getURLSyntax(club[0]), club[1]))
        database.commit()

    database.close()
    cursor.close()

    print("INITIALIZED DATABASE `UNSPAMMIFY`")
