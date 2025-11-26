import logging
from pathlib import Path

import pytest

from data_processing.graph_utils import get_graph, get_neighbor_ids, get_upstream_ids
from data_processing.file_paths import FilePaths

# Configure logging
logger = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

# Fixtures created with:
# python -m ngiab_data_cli -sfr --output_name=cat-485833 --start 2022-07-26 --end 2022-07-28 -i cat-485833

@pytest.fixture(scope="session")
def test_hydrofabric_path():
    """Return the path to the test hydrofabric geopackage."""
    test_data_path = Path(__file__).parent / "data" / "cat-485833" / "config" / "cat-485833_subset.gpkg"
    assert test_data_path.exists(), f"Test data file not found at {test_data_path}"
    return test_data_path


@pytest.fixture(scope="session")
def test_graph(test_hydrofabric_path):
    """Load the graph from the test hydrofabric data file.
    
    This fixture temporarily overrides FilePaths.conus_hydrofabric to use the test data.
    """
    # Store original path
    original_conus_path = FilePaths.conus_hydrofabric
    original_graph_path = FilePaths.hydrofabric_graph
    
    try:
        # Override with test paths
        FilePaths.conus_hydrofabric = test_hydrofabric_path
        # Use a temporary location for the pickled graph
        FilePaths.hydrofabric_graph = test_hydrofabric_path.parent / "test_igraph_network.gpickle"
        
        # Clear the cache on get_graph to force reload
        get_graph.cache_clear()
        
        # Load the graph
        graph = get_graph()
        yield graph
        
    finally:
        # Restore original paths
        FilePaths.conus_hydrofabric = original_conus_path
        FilePaths.hydrofabric_graph = original_graph_path
        get_graph.cache_clear()

class TestUpstreamIds:
    """Tests for the get_upstream_ids function."""

    def test_upstream_with_outlet(self, test_graph):
        result = get_upstream_ids("cat-485885", include_outlet=True)
        expected = {"nex-485710","wb-485885","wb-485709","wb-485884","nex-485709"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_upstream_without_outlet(self, test_graph):
        result = get_upstream_ids("cat-485885", include_outlet=False)
        expected = {"wb-485885"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"


class TestGetNeighborIds:
    """Tests for the get_neighbor_ids function."""

    def test_result_is_set_traverse_limit_1(self, test_graph):
        """Test that get_neighbor_ids returns a set."""
        logger.info("Testing that get_neighbor_ids returns a set with traverse_limit=1")
        
        result = get_neighbor_ids("cat-485712", include_outlet=True, traverse_limit=1)
        
        assert isinstance(result, set), f"Expected result to be a set, but got {type(result)}"

    def test_result_is_set_traverse_limit_2(self, test_graph):
        """Test that get_neighbor_ids returns a set."""
        logger.info("Testing that get_neighbor_ids returns a set with traverse_limit=2")
        
        result = get_neighbor_ids("cat-485712", include_outlet=True, traverse_limit=2)
        
        assert isinstance(result, set), f"Expected result to be a set, but got {type(result)}"

    def test_traverse_limit_1_with_outlet(self, test_graph):
        """Test get_neighbor_ids with traverse_limit=1 and include_outlet=True.
        
        For input name "cat-485712" with traverse_limit=1 and include_outlet=True,
        should return { ... }.
        """
        logger.info("Testing get_neighbor_ids with traverse_limit=1, include_outlet=True")
        
        result = get_neighbor_ids("cat-485712", include_outlet=True, traverse_limit=1)
        expected = {"nex-485713", "wb-485712", "wb-485880","wb-485887"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_traverse_limit_2_with_outlet(self, test_graph):
        """Test get_neighbor_ids with traverse_limit=2 and include_outlet=True.
        
        For input name "cat-485712" with traverse_limit=2 and include_outlet=True,
        should return {'nex-485713','wb-485712','wb-485711','nex-485881','nex-485882','nex-485883','nex-485886','wb-485710'}.
        """
        logger.info("Testing get_neighbor_ids with traverse_limit=2, include_outlet=True")
        
        result = get_neighbor_ids("cat-485712", include_outlet=True, traverse_limit=2)
        expected = {"nex-485713", "wb-485712", "wb-485880","wb-485887",
                    "nex-485712", "wb-485711", "wb-485881",
                    "nex-485887", "wb-485888"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_traverse_limit_1_without_outlet(self, test_graph):
        """Test get_neighbor_ids with traverse_limit=1 and include_outlet=False.
        
        When include_outlet=False, 'nex-485713' should be omitted from the result.
        Should return {'wb-485712','nex-485712','wb-485711','wb-485881'}.
        """
        logger.info("Testing get_neighbor_ids with traverse_limit=1, include_outlet=False")
        
        result = get_neighbor_ids("cat-485712", include_outlet=False, traverse_limit=1)
        expected = {"wb-485712", "nex-485712", "wb-485711", "wb-485881"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_traverse_limit_2_without_outlet(self, test_graph):
        """Test get_neighbor_ids with traverse_limit=2 and include_outlet=False.
        
        When include_outlet=False, 'nex-485713' should be omitted from the result.
        Should return {'wb-485712','nex-485712','wb-485711','wb-485881','nex-485711','nex-485881','wb-485882','wb-485710','wb-485886','wb-485883'}.
        """
        logger.info("Testing get_neighbor_ids with traverse_limit=2, include_outlet=False")
        
        result = get_neighbor_ids("cat-485712", include_outlet=False, traverse_limit=2)
        expected = {"wb-485712", "nex-485712", "wb-485711", "wb-485881", 
                    "nex-485711", "nex-485881", "wb-485882", "wb-485710", "wb-485886", "wb-485883"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_input_as_list(self, test_graph):
        """Test that get_neighbor_ids works with list input."""
        logger.info("Testing get_neighbor_ids with list input")
        
        result = get_neighbor_ids(["cat-485711","cat-485881"], include_outlet=False, traverse_limit=1)
        expected = {"wb-485711", "wb-485881", 
                    "nex-485711", "nex-485881", "wb-485882", "wb-485710", "wb-485886", "wb-485883"}
        
        logger.info(f"Result: {result}")
        logger.info(f"Expected: {expected}")
        
        assert result == expected, f"Expected {expected}, but got {result}"
       
    def test_cat_and_wb_equivalent_without_outlet(self, test_graph):
        """Test that cat- and wb- prefixed IDs return equivalent results when include_outlet=False."""
        logger.info("Testing that cat-485712 and wb-485712 return equivalent results with traverse_limit=1, include_outlet=False")
        
        result_cat = get_neighbor_ids('cat-485712', include_outlet=False, traverse_limit=1)
        result_wb = get_neighbor_ids('wb-485712', include_outlet=False, traverse_limit=1)
        
        logger.info(f"Result cat: {result_cat}")
        logger.info(f"Result wb: {result_wb}")
        
        assert result_cat == result_wb, f"Expected {result_cat}, but got {result_wb}"

    def test_cat_and_wb_equivalent_with_outlet(self, test_graph):
        """Test that cat- and wb- prefixed IDs return equivalent results when include_outlet=True."""
        logger.info("Testing that cat-485712 and wb-485712 return equivalent results with traverse_limit=1, include_outlet=True")
        
        result_cat = get_neighbor_ids('cat-485712', include_outlet=True, traverse_limit=1)
        result_wb = get_neighbor_ids('wb-485712', include_outlet=True, traverse_limit=1)
        
        logger.info(f"Result cat: {result_cat}")
        logger.info(f"Result wb: {result_wb}")
        
        assert result_cat == result_wb, f"Expected {result_cat}, but got {result_wb}"

    def test_outlet_excluded_with_false_flag(self, test_graph):
        """Test that the outlet ID is excluded when include_outlet=False."""
        logger.info("Testing that outlet is excluded when include_outlet=False")
        
        result_with_outlet = get_neighbor_ids("cat-485712", include_outlet=True, traverse_limit=1)
        result_without_outlet = get_neighbor_ids("cat-485712", include_outlet=False, traverse_limit=1)
        
        # The outlet should be in the 'with_outlet' result
        assert "nex-485713" in result_with_outlet, "Outlet 'nex-485713' should be in result when include_outlet=True"
        
        # The outlet should NOT be in the 'without_outlet' result
        assert "nex-485713" not in result_without_outlet, "Outlet 'nex-485713' should not be in result when include_outlet=False"
        
    def test_union_equals_list_input(self, test_graph):
        """Test that results from individual calls union to results from list input."""
        logger.info("Testing that union of individual results equals list input result")
        
        result_a = get_neighbor_ids("cat-485711", include_outlet=False, traverse_limit=1)
        logger.info(f"{result_a=}")
        result_b = get_neighbor_ids("cat-485881", include_outlet=False, traverse_limit=1)
        logger.info(f"{result_b=}")
        result_ab = get_neighbor_ids(["cat-485711","cat-485881"], include_outlet=False, traverse_limit=1)

        assert result_a.union(result_b) == result_ab

    def test_recursive_call_equals_depth_two(self, test_graph):
        """Test that recursively calling with depth 1 on depth 1 results equals traverse_limit=2."""
        logger.info("Testing that recursive depth 1 calls equal traverse_limit=2")
        
        result_depth_1 = get_neighbor_ids("cat-485712", include_outlet=False, traverse_limit=1)
        logger.info(f"{result_depth_1=}")
        result_depth_1_2x = get_neighbor_ids(['wb-485712', 'wb-485711', 'nex-485712', 'wb-485881'], include_outlet=False, traverse_limit=1)
        logger.info(f"{result_depth_1_2x=}")
        result_depth_2 = get_neighbor_ids("cat-485712", include_outlet=False, traverse_limit=2)
        logger.info(f"{result_depth_2=}")

        assert result_depth_1_2x == result_depth_2

        
