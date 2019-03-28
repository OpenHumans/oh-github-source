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