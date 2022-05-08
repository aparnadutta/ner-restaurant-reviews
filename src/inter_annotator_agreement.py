"""Functions for computing Cohen's kappa (𝜅), a measure of inter-annotator
agreement between exactly two annotators."""

from typing import NamedTuple
from sklearn.metrics import cohen_kappa_score

PATH = "90_UPDATED_all_annotations.txt"

DOCSTART = "-DOCSTART-"
NO_ANNOTATION = "N/A"

# 27955 27955
# June and Ayla:  0.7691149155717287
# 22625 22625
# Ayla and Aparna:  0.7214786237867662
# 35512 35512
# Aparna and June:  0.8345672763997536


class IAA(NamedTuple):
    """Immutable counts for computing IAA"""

    annotations1: list[str]
    annotations2: list[str]

    @property
    def cohen_kappa(self) -> float:
        return cohen_kappa_score(self.annotations1, self.annotations2)

    def update(self, other: "IAA") -> "IAA":
        return IAA(
            self.annotations1 + other.annotations1,
            self.annotations2 + other.annotations2
        )


# Aparna 0, June 1, Ayla 2
# Check for ONLY TWO ANNOTATORS (there are some documents with 1 and some with 3)
# Find out how many documents per pair of annotators

# Give two files of annotators
# Find overlapping reviews
# Process and calculate IAA??

# Try without O

def run():
    june_ayla = IAA([], [])
    june_ayla_no_O = IAA([], [])
    ayla_aparna = IAA([], [])
    ayla_aparna_no_O = IAA([], [])
    aparna_june = IAA([], [])
    aparna_june_no_O = IAA([], [])
    with open(PATH) as file:
        for line in file:
            # For each line of annotation (not /n or DOCSTART)
            if line != "\n" and not line.startswith(DOCSTART):
                if len(line.strip().split(" ")) == 4:
                    token, ann0, ann1, ann2 = line.strip().split(" ")
                    # MUST CHECK JUNE AND AYLA FIRST DUE TO DOC WITH THREE ANNOTATIONS
                    # Check June and Ayla
                    if ann1 != NO_ANNOTATION and ann2 != NO_ANNOTATION:
                        new = IAA([ann1], [ann2])
                        june_ayla = june_ayla.update(new)
                        if ann1 != "O" or ann2 != "O":
                            june_ayla_no_O = june_ayla_no_O.update(new)
                    # Check Ayla and Aparna
                    elif ann2 != NO_ANNOTATION and ann0 != NO_ANNOTATION:
                        new = IAA([ann2], [ann0])
                        ayla_aparna = ayla_aparna.update(new)
                        if ann2 != "O" or ann0 != "O":
                            ayla_aparna_no_O = ayla_aparna_no_O.update(new)
                    # Check Aparna and June
                    elif ann0 != NO_ANNOTATION and ann1 != NO_ANNOTATION:
                        new = IAA([ann0], [ann1])
                        aparna_june = aparna_june.update(new)
                        if ann0 != "O" or ann1 != "O":
                            aparna_june_no_O = aparna_june_no_O.update(new)
                    # else:
                    #     print("LINES WITH 0 OR 1 ANNOTATION:", line.strip())
#     Calculate IAA
    print("June and Ayla: ", june_ayla.cohen_kappa)
    print("June and Ayla, no O: ", june_ayla_no_O.cohen_kappa)
    print("Ayla and Aparna: ", ayla_aparna.cohen_kappa)
    print("Ayla and Aparna, no O: ", ayla_aparna_no_O.cohen_kappa)
    print("Aparna and June: ", aparna_june.cohen_kappa)
    print("Aparna and June, no O: ", aparna_june_no_O.cohen_kappa)


if __name__ == "__main__":
    run()
