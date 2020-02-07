from datetime import datetime
import pandas as pd
from shapely.geometry import Point
from pylandsat import Catalog, Product

catalog = Catalog()

begin = datetime(2000, 1, 1)
end = datetime(2010, 1, 1)
geom = Point(4.34, 50.85)

# Results are returned as a pandas dataframe
scenes = catalog.search(begin = begin, end = end, geom = geom, sensors = ['ETM', 'LC08'])

# Get the product ID of the scene with the lowest cloud cover
scenes = scenes.sort_values(by = 'cloud_cover', ascending = True)
product_id = scenes.index[0]

# Download the scene
product = Product(product_id)
product.download(out_dir = 'data')