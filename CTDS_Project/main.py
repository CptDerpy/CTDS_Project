from database import * # pylint: disable=W0614
import os

path = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.join(path, 'TestOpgaver')

if __name__ == "__main__":
    db = Database()

    file = input('File to test: ')
    test_file = os.path.join(test_path, file)
    # test_sig = Fingerprint(test_file).getSignatures()
    # db_sigs = db.get_all_signatures()

    # print('Similarity to article:')
    # for name, sig in db_sigs.items():
    #     sim = jaccard(test_sig, sig)
    #     if sim >= 0.001:
    #         print('{:<45}: {:.5f}'.format(name, sim))
    Fingerprint(test_file).getSubstring()

    db.close()
