import logging
import os
from datetime import datetime
from time import perf_counter

from dotenv import load_dotenv

from _model import KENEC
from errors.database import (
    DatabaseConnectionAlreadyExists,
    DatabaseConnectionError,
    DatabaseMigrationError,
)
from modal.database.util.auth import DatabaseAuth

# from _model import KENEC
# from modal.database.node import Article
from modules.database import Neo4jAdapter


def main():
    # text = """
    # Ukrainian and American officials said they had made good progress on Sunday in talks about a contentious U.S. plan to end the war with Russia, even as President Trump lashed out at Ukraine, accusing its leaders of ingratitude.
    # Mr. Trump has set a deadline of Thursday for Ukraine to agree to the 28-point peace plan, an early draft of which many Ukrainians dismissed as capitulation because it acceded to longstanding Kremlin demands.
    # The talks, which began in Geneva on Sunday, were cast as an effort to bridge the gaps, and in a joint statement released after the discussions, Ukraine and the United States both said that much had been accomplished.
    # “They reaffirmed that any future agreement must fully uphold Ukraine’s sovereignty and deliver a sustainable and just peace,” the statement read. “As a result of the discussions, the parties drafted an updated and refined peace framework.”
    # The statement added that “Ukraine and the United States agreed to continue intensive work on joint proposals in the coming days.”
    # Earlier in the day, Mr. Rubio said the American and Ukrainian teams were working through the peace plan point by point and making adjustments, “narrowing the differences and getting closer to something” that both Kyiv and Washington would be “comfortable with.”
    # He said he was “very optimistic” that an agreement could be reached “in a very reasonable amount of time.”
    # Mr. Rubio noted that “obviously the Russians get a vote here” and will “have to agree to this.” He later left Geneva to return to Washington, a State Department official said.
    # Andriy Yermak, the head of Ukraine’s delegation, had earlier spoken of “very good progress” and told reporters that discussions would continue in the days ahead.
    # The cautiously optimistic — and seemingly aligned — remarks, followed by the joint statement, came despite a lengthy missive that Mr. Trump posted on social media criticizing Ukraine, as well as its European allies, which have been largely excluded from the plan.
    # “Ukraine ‘leadership’ has expressed zero gratitude for our efforts,” Mr. Trump wrote, “and Europe continues to buy oil from Russia.”
    # He also again appeared to blame Ukraine for Russia’s full-scale invasion, saying that the war “would have NEVER HAPPENED” had there been “strong and proper” Ukrainian leadership.
    # It was not the first time that the American president had accused Ukraine of insufficient gratitude, or of responsibility for the war that Russia started. During a disastrous meeting with Mr. Zelensky in the Oval Office in February, Mr. Trump told the Ukrainian leader that he was not doing enough to thank the United States for its support.
    # Since then, Mr. Zelensky and other members of his administration have taken pains to express their thanks.
    # Mr. Zelensky did so again on Sunday in a series of statements, not long after Mr. Trump’s social media posts. Mr. Zelensky welcomed the “substantive conversations” in Geneva and appeared to respond, albeit indirectly, to the U.S. president’s latest accusations.
    # “The crux of the entire diplomatic situation is that it was Russia, and only Russia, that started this war, and it is Russia, and only Russia, that has been refusing to end it,” Mr. Zelensky wrote in one of the statements.
    # “The leadership of the United States is important, we are grateful for everything that America and President Trump are doing for security, and we keep working as constructively as possible,” he added, saying later that “tomorrow will be no less active.”
    # Ukraine’s European allies, some of whom sent representatives to Geneva to participate in the discussions, have been working to respond to the U.S. proposal and to demonstrate their continued support for Kyiv. In their statement on Sunday night, Ukraine and the United States said they would “remain in close contact with their European partners as the process advances.”
    # A draft of the U.S. peace proposal posted online last week contained many conditions that Ukraine has long rejected as unacceptable, including surrendering territory and slashing the size of its army.
    # On Saturday, the leaders of Britain, France, Germany and other countries had released a statement urging changes to the points in the plan that were most objectionable to Ukraine.
    # Ursula von der Leyen, the president of the European Commission, reasserted this on Sunday. “As a sovereign nation there cannot be limitations on Ukraine’s armed forces that would leave the country vulnerable to future attack,” she said.
    # That, she said, would also undermine European security.
    # There was no immediate comment on Sunday from the Kremlin about the talks in Geneva. An American official said earlier that plans for separate talks between the United States and Russia were underway.
    # Other diplomatic efforts are expected in the coming days.
    # President Recep Tayyip Erdogan of Turkey, who has offered to mediate between Russia and Ukraine, said he expected to speak to the Russian president, Vladimir V. Putin, on Monday about the peace efforts. And President Emmanuel Macron of France suggested that there would be a meeting involving the leaders of Britain, Canada and several other nations on Tuesday.
    # While Mr. Trump has said he wants Ukraine’s response to the peace plan by Thursday, he has left open the possibility that the deadline could be extended “if things are working well.”
    # Ukrainian and U.S. officials had already discussed changes to the 28-point plan before the meeting in Geneva, according to a Western official briefed on the talks. The working version now differs, the official said, from a version posted online on Thursday by a Ukrainian lawmaker.
    # Still, there seemed to be continued confusion about the original proposal, including among lawmakers. A group of U.S. senators said on Saturday that Mr. Rubio had told them that the document “was not the administration’s plan” but a “wish list of the Russians.”
    # The State Department said that was “blatantly false,” and Mr. Rubio also rejected the characterization, writing on social media that “the peace proposal was authored by the U.S.”
    # “It is offered as a strong framework for ongoing negotiations,” he said. “It is based on input from the Russian side. But it is also based on previous and ongoing input from Ukraine.”
    # """

    # kw_e = YakeKeywordExtractor()
    # print(kw_e.get_keywords_from_text(text))

    # kenec = KENEC(match_threshold=1)
    # art = Article(title="Bolo", content="Shitet", published_date=datetime.now())
    # print(art.__dict__)

    # Env
    load_dotenv()

    NEO4J_URI = os.getenv("NEO4J_URI", "")
    NEO4J_DATABASE_NAME = os.getenv("NEO4J_DATABASE_NAME", "")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

    print("************ Starting initialization")
    kenec = KENEC(
        ner_model="spacy_web_sm",
        db_auth=DatabaseAuth(
            uri=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE_NAME,
        ),
    )
    print("************ Completed initialization")


if __name__ == "__main__":
    main()
