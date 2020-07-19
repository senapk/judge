indexer board --base base --path board.md --gen --sort cat 
indexer board --base base --path board.md --set

indexer links --source board.md

indexer index --path Readme.md --group_by cat --sort_by title --insert_hook --insert_toc --key_filter --reverse_sort

indexer manual --source board --path Readme.md --insert_hook

indexer toc Readme.md

####
indexer board --get --path board.md
