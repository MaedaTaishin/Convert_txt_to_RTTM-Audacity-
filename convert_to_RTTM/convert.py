from typing import TextIO, Optional, Iterator
from pyannote.core import Segment

class Annotation:
    def __init__(self, segment_list, uri=None, modality=None):
        self.segment_list = segment_list
        self.uri = uri
        self.modality = modality
    
    @classmethod
    def from_records(cls, segment_list, uri=None, modality=None) -> "Annotation":
        return cls(segment_list, uri, modality)
    
    @classmethod
    def from_rttm(
        cls, rttm_file: TextIO, uri: Optional[str] = None, modality: Optional[str] = None,
    ) -> "Annotation":
        """Create annotation from rttmParameters
        ----------
        rttm_file : string,
            path to the rttm file
        uri : string, optional
            name of annotated resource (e.g. audio or video file)
        modality : string, optional
            name of annotated modality
        Returns
        -------
        annotation : Annotation
            New annotation
        """
        segment_list = []
        for line in rttm_file:
            line = line.rstrip().split(" ")
            segment_list.append(
                (
                    Segment(start=float(line[3]), end=float(line[3]) + float(line[4])),
                    int(line[2]),
                    str(line[7]),
                )
            )
        return cls.from_records(segment_list, uri, modality)
    
    def _iter_audacity(self) -> Iterator[str]:
        """Generate lines for a audacity marker file for this annotation
        Returns
        -------
        iterator: Iterator[str]
            An iterator over audacity text lines
        """
        for segment, _, label in self.segment_list:
            yield f"{segment.start:.3f}\t{segment.end:.3f}\t{label}\n"
    
    def to_audacity(self) -> str:
        """Serialize annotation as a string using Audacity format
        Returns
        -------
        serialized: str
            audacity marker string
        """
        return "".join([line for line in self._iter_audacity()])
    
    def write_audacity(self, file: TextIO):
        """Dump annotation to file using Audacity format
        Parameters
        ----------
        file : file object
        Usage
        -----
        >>> with open('file.txt', 'w') as file:
        ...     annotation.write_audacity(file)
        """
        for line in self._iter_audacity():
            file.write(line)
    
    def to_rttm(self, file: TextIO):
        """Dump annotation to file using RTTM format
        Parameters
        ----------
        file : file object
        Usage
        -----
        >>> with open('file.rttm', 'w') as file:
        ...     annotation.to_rttm(file)
        """
        for segment, _, label in self.segment_list:
            file.write(f"SPEAKER {self.uri} 1 {segment.start:.3f} {segment.duration:.3f} <NA> <NA> {label} <NA>\n")
    
    @classmethod
    def from_audacity(
        cls, audacity_file: str, uri: Optional[str] = None, modality: Optional[str] = None,
    ) -> "Annotation":
        """Create annotation from an Audacity marker file
        Parameters
        ----------
        audacity_txt_file : string,
            path to the Audacity marker file
        uri : string, optional
            name of annotated resource (e.g. audio or video file)
        modality : string, optional
            name of annotated modality
        Returns
        -------
        annotation : Annotation
            New annotation
        """
        segment_list = []
        with open(audacity_file, "r") as file:
            for line in file:
                start, end, label = line.rstrip().split("\t")
                segment_list.append(
                    (Segment(start=float(start), end=float(end)), 1, str(label))
                )
        return cls.from_records(segment_list, uri, modality)

# Example usage:
audacity_file_path = "Labels_obama_zach.txt"
rttm_file_path = "output_file.rttm"

annotation = Annotation.from_audacity(audacity_file_path)
with open(rttm_file_path, "w") as rttm_file:
    annotation.to_rttm(rttm_file)
