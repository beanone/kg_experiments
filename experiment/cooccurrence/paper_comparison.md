| Feature                             | Paper                           | Your Code                      |
| ----------------------------------- | ------------------------------- | ------------------------------ |
| Uses co-occurrence networks         | ✅ yes                           | ✅ yes                          |
| Statistical validation of edges     | ✅ (null model based)            | ✅ (approximate z-score filter) |
| Focus on lemmatized content words   | ✅ (content words, no stopwords) | ✅ (stopwords + exclusions)     |
| Graph pruning based on significance | ✅ yes                           | ✅ yes (`z > 2`)                |
| Community detection                 | ✅ hSBM + validation             | ✅ hSBM + greedy modularity     |
| Multi-document input                | ✅ yes                           | ✅ yes                          |


| Feature                                   | Paper                          | Your Code                                     | Suggested Fix                                        |
| ----------------------------------------- | ------------------------------ | --------------------------------------------- | ---------------------------------------------------- |
| **Formal null model**                     | Configuration model + p-values | Approximate z-score only                      | Use actual null model (optional)                     |
| **Word lemmatization**                    | Yes                            | ❌ (lowercasing only)                          | Add lemmatization with spaCy                         |
| **POS filtering (noun/adjective)**        | Yes                            | ❌                                             | Filter by POS in `preprocess()`                      |
| **Multiple hSBM levels**                  | Yes (hierarchical blocks)      | ❌ (flat output from `minimize_blockmodel_dl`) | Use `get_levels()` or `state.draw()`                 |
| **Document-word bipartite model**         | Optional in paper              | ❌                                             | Requires custom implementation                       |
| **Topic-term and topic-document mapping** | Explicit in paper              | ❌                                             | Can extract from node labels + community assignments |

