from ...utils import Metadata, File


DESC = Metadata(
    "LASLA-ENC",
    "lat",
    ["Thibault Clérice"],
    "Model trained on LASLA data without disambiguation",
    "https://github.com/chartes/deucalion-model-lasla"
)

DOWNLOADS = [
    File("https://github.com/chartes/deucalion-model-lasla/raw/master/latin-straight.json", "latin-straight.json"),
    File("https://github.com/chartes/deucalion-model-lasla/raw/master/latin-pos.json", "latin-pos.json"),
    File("https://github.com/chartes/deucalion-model-lasla/raw/master/latin-needs.json", "latin-needs.json"),
    File("https://github.com/chartes/deucalion-model-lasla/raw/master/model.tar", "model.tar")
]

