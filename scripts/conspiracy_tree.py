from pydantic_validation import InternalNode
import pydantic
conspiracy_tree = {
    "node": "Conspiracy Theories",
    "children": [
        {
            "node": "Aviation",
            "children": [
                {"node": "Chemtrails"},
                {"node": "Black Helicopters"},
                {"node": "Korean Airline 007"},
                {"node": "Malaysia MH370"},
                {"node": "Malaysia MH 17"},
            ],
        },
        {
            "node": "Economics and Business and Society",
            "children": [
                {"node": "NESARA"},
                {"node": "Deepwater Horizon"},
                {"node": "New Coke"},
                {
                    "node": "New World Order",
                    "children": [
                        {"node": "Illuminati"},
                        {"node": "Beyonce"},
                        {"node": "Whitney Houston"},
                    ],
                },
                {"node": "Denver Airport"},
                {"node": "George Soros"},
                {"node": "Freemasonry"},
                {"node": "Ust akil (Master Mind)"},
                {"node": "Hollywood is turning your kids gay"},
                {"node": "Drug Trafficking"},
                {"node": "McDonald"},
            ],
        },
        {
            "node": "Government and Politics",
            "children": [
                {
                    "node": "Covered Up Deaths",
                    "children": [
                        {"node": "Paul McCartney"},
                        {"node":"Muhammadu Buhari"},
                        {"node":"Avril Lavigne"},
                    ],
                },
                {"node": "Death Panel"},
                {
                    "node": "9/11",
                    "children": [
                        {"node": "Anti-islami"},
                        {"node":"Loose Chain Films"},
                    ],
                },
                {
                    "node": "Deaths",
                    "children": [
                        {"node": "Abraham Lincoln"},
                        {"node": "Martin Luther King Jr."},
                        {"node": "Eric V"},
                        {"node": "Dmitry Ivanovich"},
                        {"node": "Sheikh Rahman"},
                        {"node": "Yitzhak Rabin"},
                        {"node": "Zachary Taylor"},
                        {"node": "Yitzhak Rabin"},
                        {"node": "George S. Patton"},
                        {"node": "Diana Princess of Wales"},
                        {"node": "Dag Hammarskjold"},
                        {"node": "Kurt Kobain"},
                        {"node": "Michael Jackson"},
                        {"node": "Marilyn Monroe"},
                        {"node": "TuPac Shakur"},
                        {"node": "Wolfgang Amadeus Mozart"},
                        {"node": "John Lennon"},
                        {"node": "Jimi Hendrix"},
                        {"node": "Notorius B.I.G"},
                        {"node": "Pope John Paul I"},
                        {"node": "Jill Dando"},
                        {"node": "Olof Palme"},
                        {"node": "Chester Bennington"},
                        {"node": "Paul Walker"},
                        {"node": "David Kelly"},
                        {"node": "Subhas Chandra Bose"},
                        {"node": "Sushant Singh Rajput"},
                        {"node": "Elvis Presley"},
                        {"node": "Adolf Hitler"},
                        {"node": "Lord Lucan"},
                        {"node": "Madeline McCann"},
                        {"node": "Seth Rich"},
                        {"node": "Nero"},
                    ],
                },
                {
                    "node": "Shootings",
                    "children": [
                        {"node": "Sandy Hook"},
                        {"node": "Pizza Gate"},
                        {"node": "J.F. Kennedy"},
                        {"node": "Sutherland Springs"},
                        {"node": "Parkland Shooting"},
                    ]
                
                },
                {
                    "node": "Espionage",
                    "children": [
                        {"node": "Israel Animal Spying"},
                    ]
                },
                {
                    "node": "Stolen Election",
                    "children": [
                        {"node": "Harold Wilson"},
                        {"node": "Malala Yousafzi"}
                    ]
                },
                {"node": "Crisis Actors"},
                {"node": "Deep State"},
                {"node": "Clintons "},
                {"node": "Jeffrey Epstein"},
                {"node": "Federal Emergency Management Agency"},
                {"node": "African National Congress"},
                {"node": "Barack Obama"},
                {"node": "Cultural Marxism"},
                {
                    "node": "QAnon",
                    "children": [
                        {"node": "Russian interference"},
                        {"node": "Wayfair"},
                        {"node": "Italygate"},
                        {"node": "Satanic Ritual Abuse"},
                        {"node": "Adeno chrome"},
                        
                    ]
                },
                {
                    "node": "Donald Trump",
                    "children": [
                        {"node": "Election - Ukraine - Biden"},
                        {"node": "Hurricane Maria"}
                    ]
                },
                {
                    "node": "Joe Biden",
                    "children": [
                        {"node":"Ukraine Gas Company"},
                    ]
                },
                {
                    "node": "Body Double",
                    "children": [
                        {"node":"Melania Trump"},
                    ]
                },
                {"node": "False Flag Operations"},
                {"node": "Ukraine Bioweapons"},
                {"node": "Malcom X"},
                {"node": "October Surprise"},
                {"node": "Nazis on the Moon"},
                {"node": "Buckingham Naked Boy"},
                {"node": "Jimmy Savile"},
                {"node": "Jade Helm"},
                {"node": "Room 641a"},
                {"node": "German Coup"},
 
            ],
        },
        {
            "node": "Medical (Big Pharma)",
            "children": [
                {"node": "Chicken Farm"},
                {"node": "Fluoridation"},
                {
                    "node": "Viruses and Vaccines",
                    "children": [
                        {"node": "Zika"},
                        {   "node": "HIV",
                            "children": [
                                {
                                    "node": "Artificial Diseases",
                                    "children": [
                                        {"node": "HGV"},
                                        {"node": "ADHD"},
                                    ],
                                },
                            ],
                        },
                        {"node": "Ebola"},
                        {
                            "node": "Covid-19",
                            "children": [
                                {"node": "Bill Gates as Scapegoat"},
                            ]
                        },
                        {"node": "MMR"},
                        {"node": "DPT"},
                        {"node": "HPV"},
                        {"node": "Smallpox"},
                        {"node": "Polio"},
                        {"node": "Microchips"},
                        {"node": "Flu Shot"},
                    ],
                },
                {"node": "Cancer"},
                {"node": "Alternative Therapy Suppression"},
                
            ],
        },
        {
            "node": "Sports",
             "children": [
                {
                    "node": "Boxing",
                    "children":[
                        {"node":"Ali-Liston Fight"},
                        {"node":"Bradley-Pacquiao"}
                    ]
                },
                {"node": "Shregar Race-horse"},
                {"node": "Rigged Selection Processes"},
                {"node": "Ronaldo 1998 World Cup"},
                {"node": "New England Patriots"},
                
            ],
        },
        {
            "node": "Outer Space",
            "children": [
                {"node": "Area 51"},
                {"node": "Moon Landing"},
                {"node": "UFO"},
                {"node": "Lost Cosmonauts"},
                {"node": "12th Planet"},
                {"node": "Men in Black"},
                {
                    "node": "Reptilians",
                    "children": [ {"node": "Bush family, Margaret Thatcher, Bob Hope, and the British Royal Family"}]
                },
                {"node": "Dead Cattle"},
                {"node": "Ancient Astronauts"},
                {"node": "Alien Mummy"},
                {"node": "Apollo 17"},
                {"node": "Black Holes"},
            ],
        },
        {
            "node": "Science and Technology",
            "children": [
                {"node": "5G Phones"},
                {"node": "MKUltra"},
                {
                    "node": "Earth",
                    "children": [
                        {"node": "Global Warming"},
                        {"node": "Flat Earth"},
                        {"node": "Climate Change"},
                        {"node": "Hollow Earth"},
                    ],
                },
                {"node": "HAARP"},
                {"node": "RFID"},
                {"node": "Technology Suppression"},
                {"node": "Weaponry"},
                {"node": "Targeted Individuals"},
                {"node": "False History"},
                
            ],
        },
        {
            "node": "Race and Religion",
            "children": [
                {
                    "node": "Antisemitism",
                    "children": [
                        {"node": "Jewish Space Lasers"},
                        {"node": "The Protocols of the Elders of Zion"},
                        {"node": "Holocaust Denial"},
                        {"node": "Rothschild Central Bank"},
                    ],
                },
                {"node": "Anti-Armenianism"},
                {"node": "Anti-Bahá'ísm"},
                {"node": "Anti-Catholicism"},
                {"node": "Antichrist"},
                {"node": "Bible and Jesus"},
                {"node": "Islam"},
                {
                    "node": "Racism",
                    "children": [
                        {"node": "Great Replacement"},
                        {
                            "node": "White Genocide",
                            "children": [ {"node": "Great Replacement"}]
                        },
                        {"node": "Black Genocide"},
                    ],
                
                },
                {"node": "Paul the Apostle"}
               
            ],
        },
    ],
}


def children(n: dict) -> list:
    return n.get("children", [])


def prefix_match(s: dict, t: dict) -> bool:
    #stessa radice
    # lower per rendere case insensitive
    if s["node"].lower() != t["node"].lower():
        return False
    return all(
        any(prefix_match(sc, tc) for tc in children(t))
        for sc in children(s)
    )


def is_valid_subtree(sub: dict, tree: dict) -> bool:
    #validazione struttura
    try:
        InternalNode.model_validate(sub)  
    except pydantic.ValidationError:
        return False

    return prefix_match(sub, tree)


