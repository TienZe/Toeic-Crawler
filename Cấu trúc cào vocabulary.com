* Trang này chứa nhiều collection, mỗi collection có thể chứa những collection khác, và cuối cùng là chứa những list từ vựng

* Cào collection:
1. Grade:
- Super collection: .item-vocab-list:not(.is-image)
- Child collection: .unit.type_work.with-icon
                    .unit.type_collection.with-icon
                    
2. Literature:
- Super collection: .unit-list .type_work
                    .unit-list .type_collection.style-feature
                    
3. Non-fiction:
- Super collection: giống Literature
4. Test-Prep:
- Super Collection: .unit-list .type_collection.style-feature
                    .unit-list .type_collection.style-items-hidden

* Cào thông tin của 1 collection đơn (chỉ chứa những list từ vựng)
- title: .summary-panel .title-actions-stats .title .title
- subtitle: .summary-panel .title-actions-stats .subtitle
- description: .summary-panel .title-actions-stats blockquote
- thumbnail: .summary-panel .summary .header-img img
- book_purchase_link: .summary-panel .title-actions-stats a.buy-book
- author: .summary-panel .title-actions-stats .authors a



** synthetic dataset, instruction fine tuning
