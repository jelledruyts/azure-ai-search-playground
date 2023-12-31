using Azure.AISearch.WebApp.Models;

namespace Azure.AISearch.WebApp.Services;

public class SearchRequestHandler
{
    private readonly IEnumerable<ISearchService> searchServices;

    public SearchRequestHandler(IEnumerable<ISearchService> searchServices)
    {
        this.searchServices = searchServices;
    }

    public async Task<SearchResponse?> HandleSearchRequestAsync(SearchRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Query))
        {
            return null;
        }
        // Send the request to each registered search service that can handle the request
        // and return the first valid response.
        foreach (var searchService in this.searchServices.Where(s => s.CanHandle(request)))
        {
            try
            {
                var searchResponse = await searchService.SearchAsync(request);
                if (searchResponse != null)
                {
                    return searchResponse;
                }
            }
            catch (Exception ex)
            {
                return new SearchResponse { Error = ex.Message };
            }
        }
        return new SearchResponse { Error = "The search request couldn't be handled by any registered search service." };
    }
}