# Session Plan: DANDI 000019

This plan selects one NWB file for the first local inspection pass. The selected file is small enough to download before working through the larger sessions.

## Selected Asset

| Field | Value |
| --- | --- |
| DANDI version | `0.220126.2148` |
| Selection rule | smallest asset overall |
| Path | `sub-EC9/sub-EC9_ses-EC9-B15.nwb` |
| Subject | EC9 |
| Session | EC9-B15 |
| Size | 532.3 MiB |
| Asset ID | `4e4287f2-b557-4f30-a2d6-932f18c3e915` |
| Download endpoint | `https://api.dandiarchive.org/api/assets/4e4287f2-b557-4f30-a2d6-932f18c3e915/download/` |
| Local path | `data/raw/sub-EC9/sub-EC9_ses-EC9-B15.nwb` |

## Smallest Candidate Assets

| Path | Subject | Session | Size |
| --- | --- | --- | ---: |
| `sub-EC9/sub-EC9_ses-EC9-B15.nwb` | EC9 | EC9-B15 | 532.3 MiB |
| `sub-GP31/sub-GP31_ses-GP31-B65.nwb` | GP31 | GP31-B65 | 1.0 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B1.nwb` | GP31 | GP31-B1 | 1.1 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B21.nwb` | GP31 | GP31-B21 | 1.2 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B63.nwb` | GP31 | GP31-B63 | 1.2 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B4.nwb` | GP31 | GP31-B4 | 1.2 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B67.nwb` | GP31 | GP31-B67 | 1.3 GiB |
| `sub-GP31/sub-GP31_ses-GP31-B2.nwb` | GP31 | GP31-B2 | 1.4 GiB |

## Inspection Checklist

- Open the NWB file without loading full data arrays into memory.
- List acquisition objects, processing modules, intervals, and electrode metadata.
- Identify trial labels and timing fields needed for syllable decoding.
- Save a short inspection report before extracting high-gamma features.
