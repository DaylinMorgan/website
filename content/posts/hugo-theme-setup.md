+++ 
draft = true
date = 2021-01-16T12:38:07-06:00
title = "How I adapted Hugo to build and style my personal website"
slug = "" 
tags = []
categories = []
description = ""
+++


In order to personalize the [theme](https://github.com/naro143/hugo-coder-portfolio) I chose for my website, I initially forked the project on github and placed it in the `themes/` directory of my website repo using `git submodule add`. I made a few minor changes to the html's and css, but ultimately decided it would be simpler to leave the theme repo in the same state as it's main repo. Hugo gives priority to the layouts found in the parent directory. See [here](https://gohugo.io/templates/lookup-order/) for an explanation of template lookup order in the Hugo documenation.

As such, I will summarize here, at the time of creation, the changes I made to suit coder-portfolio to own my website. I may update this post or create a new post if I make more drastic changes to the theme or my own layouts.

The first thing I wanted to change about the theme was to make the avatar or profile image found on the home page much larger. Initially I changed this in the `static/css/style.min.css`. Unaware of how difficult to see this change in version control would be. Luckily, this theme has designed its base page layout `baseof.html` to inlcude a call from `config.toml` for custom css. So I created a seperate `custom.css` within the `static/css/` directory to make the necessary changes to the `.avatar` class, shown below. Since this style sheet is loaded after the themes style sheets it will override any classes shared between them. 

```css
.avatar img {
    max-width: 100%;
    width: 80rem;
    height: auto;
    border-radius: 50%;
  }
```

Next, I needed to make some changes to the `layouts/_default/baseof.html` layout to ensure properly rendered icons. The defult theme utilized conditionals from Hugo to determine if the stylesheet for font awesome should be loaded. Since I was using icons and loading this additionaly stylesheet would always occur, I initially opted to remove the conditional. However, upon further examination I realized I simply needed to add the line `faIcons = true` to my `config.toml`. 

```html
{{ if or (.Site.Params.snsShare) (.Site.Params.faIcons) }}
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
{{ end }}
```

Finally, I wanted to change the was the about section was generated to allow me to define my education in my `config.toml` and render them at the bottom of the about page. Since, this would require changing the layout used from the themes generic `page.html` layout. I made a custom about section layout `layouts/static/about.html`. In the event I develop other static pages for my site I will also leave their layouts here. In order to ensure Hugo preferred this layout I add the line `type = "static"` to the front matter of my `about.md`. I took the `single.html` from my theme and added the following lines.

```html
<section class="container page">
    <article>
        <header>
            <h1>{{ .Title }}</h1>
        </header>

        {{ .Content }}

    </article>
    <H2><i class="fa fa-graduation-cap" aria-hidden="true"></i>Education </H2>
    {{ range .Site.Params.education.list }}
    <dl>
        <dt>{{ .degree }}</dt>
        <dd class="mb-0 ml-3">{{ .dates }} &middot; {{ .college }}</dd>
        {{ if .thesis_title }}
        <dd class="mb-0 ml-3">Thesis: {{ .thesis_title}} </dd>
        {{ end }}
    </dl>
    {{ end }}
</section>
```

Knowing my self I am likely to make more minor tweaks (light and dark mode maybe) to this theme possibly also utilizing the built in sharing features. It's also possible I may overhaul the entire site with an entirely different theme. In that event I will be sure to update this post with the changes I make. 
