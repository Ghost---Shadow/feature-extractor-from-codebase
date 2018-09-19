# Feature extractor from codebase

Lets say you git cloned a large open source repository which has a lot of features. The total bundle size of the repository is very large but you only need 1 feature. So, I made a python script that when supplied with a class name (right now its Java only), copies that class and all its dependencies (recursively) to a different folder.
