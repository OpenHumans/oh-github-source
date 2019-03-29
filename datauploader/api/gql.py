from demotemplate.settings import rr


GITHUB_GRAPHQL_BASE = 'https://api.github.com/graphql'

def graphql_query(github_access_token, query):
    auth_header = {"Authorization": "Bearer " + github_access_token}
    response = rr.post(GITHUB_GRAPHQL_BASE, json={'query': query}, headers=auth_header, realms=['github'])
    return response

# a test query for graphql
TEST_QUERY = """ 
   { 
     viewer {
       login  
       url
       id
       email
       bio
       company
       companyHTML
       pullRequests{
         totalCount
       }
       gists {
       totalCount
   }
     company
     repositoriesContributedTo(first:10){
       totalCount
       edges{
         node{
           name
           id
           forkCount
           issues(first:5){
             totalCount
             edges{
               node{
                 author{
                   resourcePath
                 }
                 assignees{
                   totalCount
                 }
               }
             }
           }
         }
       }
     }
     repositories(isFork:false, first:10){
       totalCount
       edges{
         node{
           name
           id
           forkCount
           issues(first:10){
             totalCount
             edges{
               node{
                 author{
                   resourcePath
                 }
                 assignees{
                   totalCount
                 }
                 participants{
                   totalCount
                 }
               }
             }
           }
         }
       }
     }
     forked: repositories(isFork:true, first:10){
       totalCount
         edges{
           node{
             name
             id
             forkCount
           }
         }
       }
     starredRepositories(first:10) {
       totalCount
       edges {
         node {
           name
           id
           forkCount
         }
       }
     }
     following(first:10){
       totalCount
       nodes{
         name
         id
         url
       }
     }
     followers(first:10) {
       edges {
         node {
           name
           id
           url
         }
       }
     }
   }
 }      
 """