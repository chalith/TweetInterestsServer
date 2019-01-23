import pexpect, os, logging, time, sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class StanfordCoreNLP():
    def __init__(self, corenlp_path=None):
        jars = ["stanford-corenlp-3.9.2.jar",
                "stanford-corenlp-3.9.2-models.jar",
                "joda-time.jar",
                "xom.jar",
                "jollyday.jar"]
       
        if not corenlp_path:
            corenlp_path = "./stanford-corenlp-full-2018-10-05/"
        
        java_path = "java"
        classname = "edu.stanford.nlp.pipeline.StanfordCoreNLP"
        props = "-annotators tokenize,ssplit,pos,lemma,ner,parse -ner.useSUTime 0" 
        
        jars = [corenlp_path + jar for jar in jars]
        for jar in jars:
            if not os.path.exists(jar):
                logger.error("Error! Cannot locate %s" % jar)
                sys.exit(1)
        
        start_corenlp = "%s -Xmx1800m -cp %s %s %s" % (java_path, ':'.join(jars), classname, props)
        logger.debug(start_corenlp)
        self.corenlp = pexpect.spawn(start_corenlp)
        
        self.corenlp.expect("done.", timeout=20) # Load pos tagger model (~5sec)
        print ("Loading Models: 1/5", end="\r")
        self.corenlp.expect("done.", timeout=200) # Load NER-all classifier (~33sec)
        print ("Loading Models: 2/5", end="\r")
        self.corenlp.expect("done.", timeout=600) # Load NER-muc classifier (~60sec)
        print ("Loading Models: 3/5", end="\r")
        self.corenlp.expect("done.", timeout=600) # Load CoNLL classifier (~50sec)
        print ("Loading Models: 4/5", end="\r")
        self.corenlp.expect("done.", timeout=200) # Loading PCFG (~3sec)
        print ("Loading Models: 5/5", end="\r")
        self.corenlp.expect("Entering interactive shell.")

    def parse(self,text):
        while True:
            try:
                self.corenlp.read_nonblocking (4000, 0.3)
            except pexpect.TIMEOUT:
                break

        self.corenlp.sendline(text)

        max_expected_time = min(40, 3 + len(text) / 20.0)
        end_time = time.time() + max_expected_time

        incoming = ""
        while True:
            try:
                incoming += self.corenlp.read_nonblocking(2000, 1).decode("utf-8") 
                if "\nNLP>" in incoming:
                    break
                time.sleep(0.0001)
            except pexpect.TIMEOUT:
                if end_time - time.time() < 0:
                    logger.error("Error: Timeout with input '%s'" % (incoming))
                    break
                else:
                    continue
            except pexpect.EOF:
                break

        return incoming