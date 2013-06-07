from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='gu.plone.fresnel',
      version=version,
      description="Plone Fresnel Tools",
      # long_description=open("README.txt").read() + "\n" +
      #                  open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'':'src'},
      namespace_packages=['gu', 'gu.plone' ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'gu.plone.rdf',
      ],
      extras_require={
          'test': ['plone.app.testing', ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
