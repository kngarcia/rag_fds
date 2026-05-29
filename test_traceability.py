import unittest
from src.chunker.models import Chunk
from src.parser.traceability_builder import TraceabilityBuilder

class TestTraceabilityBuilder(unittest.TestCase):

    def test_associate_images(self):
        chunks = [
            Chunk(chunk_id="1_0", content="test", section_number="1", section_title="ID", source_file="fds.pdf", chunk_index=0, page_start=1)
        ]
        images = [
            {"page": 1, "filename": "img1.png"},
            {"page": 2, "filename": "img2.png"}
        ]
        
        updated_chunks = TraceabilityBuilder.associate_images_to_chunks(chunks, images)
        self.assertEqual(len(updated_chunks[0].metadata["images"]), 1)
        self.assertEqual(updated_chunks[0].metadata["images"][0], "img1.png")

    def test_format_citation(self):
        chunk = Chunk(chunk_id="2_0", content="test", section_number="2", section_title="Hazards", source_file="fds.pdf", chunk_index=0, page_start=3)
        citation = TraceabilityBuilder.format_citation(chunk)
        self.assertIn("fds.pdf", citation)
        self.assertIn("pág. 3", citation)
        self.assertIn("Sección 2", citation)

if __name__ == "__main__":
    unittest.main()
