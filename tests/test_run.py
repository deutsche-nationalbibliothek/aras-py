from httpx import Response
from textwrap import dedent
import pytest

from aras_py.run import get_stream

test_base_url = "http://dnb-test-aras/"

@pytest.mark.respx(base_url=test_base_url)
def test_aras_get_stream(respx_mock):

    example_content_0 = "One example WARC content"
    example_content_1 = "Another example WARC content"

    repository = "example_warc"
    idn = "1234567890"

    mets_file = """
    <file ID="{id}" MIMETYPE="{mime_type}" CREATED="2018-10-01T07:15:08" SIZE="{size}">
        <FLocat LOCTYPE="URL" xlink:href="{href}"/>
    </file>
    """
    # id = 0
    # mime_type = "application/gzip"
    # size = 180641790
    # href = "DNB-oia-02879-20180502192019-66e7eed6-3d4e-e811-a3f5-d4ae528b7600-00000-DWA-DA2.warc.gz"

    mock_files = [
        mets_file.format(id=0, mime_type="text/plain", size=len(example_content_0.encode("utf8")), href="example_0.txt"),
        mets_file.format(id=1, mime_type="text/plain", size=len(example_content_1.encode("utf8")), href="example_1.txt")
    ]

    #/access/repositories/example_warc/artifacts/1234567890/objects
    respx_mock.get(f"/access/repositories/{repository}/artifacts/{idn}/objects").mock(return_value=Response(200, text=dedent(f"""
        <?xml version='1.0' encoding='UTF-8'?>
        <mets xmlns="http://www.loc.gov/METS/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">
            <metsHdr CREATEDATE="2024-07-29T12:32:44" RECORDSTATUS="draft">
                <agent ROLE="CREATOR" TYPE="ORGANIZATION">
                    <name>Deutsche Nationalbibliothek</name>
                </agent>
            </metsHdr>
            <fileSec>
                <fileGrp>
                    {"".join({file for file in mock_files})}
                </fileGrp>
            </fileSec>
            <structMap>
                <div/>
            </structMap>
        </mets>
        """).strip()))

    respx_mock.get(f"/access/repositories/{repository}/artifacts/{idn}/objects/0").mock(return_value=Response(200, text=example_content_0))
    respx_mock.get(f"/access/repositories/{repository}/artifacts/{idn}/objects/1").mock(return_value=Response(200, text=example_content_1))

    stream_iter = get_stream(test_base_url, repository, idn)

    name, stream, metadata = next(stream_iter)
    with stream() as bytes_io:
        bytes_io.read() == example_content_0.encode("utf-8")
    name, stream, metadata = next(stream_iter)
    with stream() as bytes_io:
        bytes_io.read() == example_content_1.encode("utf-8")
