from dataclasses import dataclass
from pathlib import Path
import os


WORK_ROOT = Path(os.environ.get("MARGOT_WORK_ROOT", "/leonardo_work/IscrC_MARGOT/igugliel"))
SCRATCH_ROOT = Path(os.environ.get("MARGOT_SCRATCH_ROOT", "/leonardo_scratch/fast/IscrC_MARGOT"))


@dataclass(frozen=True)
class DatasetPaths:
    """Tutti i path derivati per un singolo dataset video"""
    name: str

    @property
    def raw_videos(self) -> Path:
        return WORK_ROOT / "dataset" / self.name

    @property
    def results(self) -> Path:
        return WORK_ROOT / "classification_results" / self.name

    @property
    def processed(self) -> Path:
        return SCRATCH_ROOT / "processed_data" / self.name

    @property
    def iframes(self) -> Path:
        return self.processed / "iframes"

    @property
    def iframes_frames(self) -> Path:
        """Sottocartella frames dentro iframes."""
        return self.iframes / "frames"

    @property
    def shotbased(self) -> Path:
        return self.processed / "frames_shotbased"

    @property
    def shotbased_frames(self) -> Path:
        """Sottocartella frames dentro frames_shotbased."""
        return self.shotbased / "frames"

    @property
    def trnsntv2(self) -> Path:
        return self.processed / "trnsntv2"

    @property
    def trnsntv2_frames(self) -> Path:
        return self.trnsntv2 / "frames"

    @property
    def transcript_timestamped(self) -> Path:
        return self.processed / "transcript" / "timestamped_transcript"

    @property
    def transcript_simple(self) -> Path:
        return self.processed / "transcript" 

    @property
    def concat_shotbased(self) -> Path:
        return self.processed / "concat" / "shotbased"

    @property
    def concat_iframes(self) -> Path:
        return self.processed / "concat" / "iframes"

    @property
    def concat_trnsntv2(self) -> Path:
        return self.processed / "concat" / "trnsntv2"

    def ensure_dirs(self, which: tuple[str, ...] = ()) -> None:
        """Crea le cartelle di output se non esistono."""
        targets = which or ("results", "iframes", "iframes_frames","shotbased","shotbased_frames","trnsntv2",
                            "trnsntv2_frames","transcript_timestamped", "transcript_simple",
                             "concat_shotbased", "concat_iframes", "concat_trnsntv2")
        for attr in targets:
            getattr(self, attr).mkdir(parents=True, exist_ok=True)

#starting samples
CT_VIDEOS = DatasetPaths("CT_videos") #166 video conspiracy
VIDEOS_SAMPLE_100 = DatasetPaths("videos_sample_100") # 100 video non-conspiracy
VIDEOS_SAMPLE_1000 = DatasetPaths("videos_sample_1000") # 1000 video non conspiracy
CT_NOVTT = DatasetPaths("CT_NOVTT_video") # 1000 video conspiracy

#samples i created
CT_TMP = DatasetPaths("ct_tmp")
MIXED_SAMPLE_1000 = DatasetPaths("mixed_sample_1000")
BALANCED_SAMPLE_2K = DatasetPaths("balanced_sample_2k")
BALANCED_SAMPLE_200 = DatasetPaths("balanced_sample_200")
