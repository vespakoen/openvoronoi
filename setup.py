from skbuild import setup

setup(
  name='openvoronoi',
  packages=['openvoronoi'],
  package_dir={'openvoronoi': 'src/pythonlib/openvoronoi'},
  include_package_data=True,
  zip_safe=False,
  python_requires='>=3.6',
)
