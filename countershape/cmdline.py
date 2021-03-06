import os.path
import sys
import argparse

import logging

from . import doc, blog, analysis, model


def main():
    parser = argparse.ArgumentParser(
        description = "Renders a Countershape documentation tree."
    )
    parser.add_argument(
        "-o", "--option", type=str,
        action="append", dest="options",
        default = [],
        help="Add option to document namespace."
    )
    parser.add_argument(
        "-d", "--dummy",
        action="store_true", dest="dummy", default=False,
        help="Perform a dummy run - don't render any files."
    )
    group = parser.add_argument_group("Analysis")
    group.add_argument(
        "-s", "--structure",
        action="store_true", dest="structure", default=False,
        help="Show site structure."
    )
    group.add_argument(
        "--blog-tags",
        action="store_true", dest="blogtags", default=False,
        help="Show blog tag histogram."
    )
    group.add_argument(
        "--blog-notags",
        action="store_true", dest="blognotags", default=False,
        help="Show blog posts with no tags."
    )
    group.add_argument(
        "--blog-has-option",
        action="store", type=str, dest="bloghasoption", default=False,
        help="Show blog posts with option."
    )
    group.add_argument(
        "--blog-has-no-option",
        action="store", type=str, dest="bloghasnooption", default=False,
        help="Show blog posts without option."
    )
    group.add_argument(
        "src",
        help="Source directory"
    )
    group.add_argument(
        "dst",
        help="Destination directory",
        nargs="?"
    )

    args = parser.parse_args()

    analysis_options = [
        "structure",
        "blogtags",
        "blognotags",
        "bloghasoption",
        "bloghasnooption"
    ]

    if any(getattr(args, i) for i in analysis_options):
        if args.dst:
            parser.error("Analysis options don't take a destination.")
    else:
        if not args.dst:
            parser.error("Render destination required.")
        if os.path.abspath(args.dst) == os.path.abspath(args.src):
            parser.error(
                "Refusing to render documentation source onto itself."
            )

    d = doc.Doc(args.src, args.options)
    if args.structure:
        d.root.dump()
    elif args.blogtags:
        analysis.blog_tags(d)
    elif args.blognotags:
        analysis.blog_notags(d)
    elif args.bloghasoption:
        analysis.blog_has_option(d, args.bloghasoption)
    elif args.bloghasnooption:
        analysis.blog_has_no_option(d, args.bloghasnooption)
    elif not args.dummy:
        def render():
            d = doc.Doc(args.src, args.options)
            try:
                d.render(args.dst)
            except model.exceptions.ApplicationError, v:
                print >> sys.stderr, "Error in %s"%v.page.src
                print >> sys.stderr, "\t", v
                return
            lst = filter(
                lambda x: isinstance(x, blog.Post), d.root.preOrder()
            )
            for i in lst:
                if i.changed:
                    print >> sys.stderr, "Rewriting %s"%i.src
                    i.rewrite()
            return d

        render()
