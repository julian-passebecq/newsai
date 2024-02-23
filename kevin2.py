from usp.tree import sitemap_tree_for_homepage

tree = sitemap_tree_for_homepage('https://www.kevinrchant.com/')
print(tree)

# all_pages() returns an Iterator
for page in tree.all_pages():
    print(page)