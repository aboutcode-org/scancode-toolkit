use SVG::Box;

enum SVG::Plot::AxisPosition <Zero SmallestValue LargestValue>;

unit class SVG::Plot;
has $.height            = 300;
has $.width             = 500;
has $.fill-width        = 0.80;
has $.label-font-size   = 12;
has $.legend-font-size  = $!label-font-size;

has @.legends is rw;
has @.values  is rw;
has @.x       is rw;    # only used in 'xy' variants
has @.labels  is rw = @!values[0].keys;
has @.links   is rw;

has $.plot-width        = $!width  * 0.80;
has $.plot-height       = $!height * (@!legends ?? 0.5 !! 0.65);

has $.title             = '';

has &.x-tick-step       = -> $max {
    10 ** $max.log10.floor  / 2
}

has &.y-tick-step       = -> $max {
    10 ** $max.log10.floor  / 2
}

has $.max-x-labels      = $!plot-width / (1.5 * $!label-font-size);

has $.label-spacing     = ($!height - $!plot-height) / 20;

has @.colors = <#3333ff #ffdd66 #aa2222 #228844 #eebb00 #8822bb>;

has $.min-y-axis        = Inf;

multi method plot(:$full = True, :$stacked-bars!) {

    my $label-skip = ceiling(@.values[0] / $.max-x-labels);
    my $max_x      = @.values[0].elems;

    # maximum value of the sum over each column
    my $max_y      =  [max] @.values[0].keys.map: {
        [+] @.values.map: -> $a { $a[$_] }
    };
    my $datasets   = +@.values;

    my $step_x     = $.plot-width  / $max_x;
    my $step_y     = $.plot-height / $max_y;

    my @svg_d = gather {
        my $bar-width = $.fill-width * $step_x;
        for flat @.values[0].keys Z @.labels -> $k, $l {
            my $y-offset  = 0;
            for ^$datasets -> $d {
                my $v = @.values[$d][$k];
                my $p = 'rect' => [
                    :y(-$v * $step_y - $y-offset),
                    :x($k * $step_x),
                    :width($bar-width),
                    :height($v * $step_y),
                    :style("fill:{ @.colors[$d % *] }; stroke: none"),
                ];
                $y-offset += $v * $step_y;
                take |$.linkify($k, $p);
            }
        }

        $.plot-x-labels(:$step_x, :$label-skip);
        $.y-ticks(0, $max_y, $step_y);
    }

    my $svg = $.apply-standard-transform(
        @svg_d,
        @.eyecandy(),
    );

    @.wrap-in-svg-header-if-necessary($svg, :wrap($full));
}

# snip...

=begin Pod

=head1 NAME

SVG::Plot - simple SVG bar charts

=head1 VERSION

$very_early

=head1 SYNOPSIS

    use SVG;
    use SVG::Plot;

    my @d1 = (0..100).map: { sin($_ / 10.0) };
    my @d2 = (0..100).map: { cos($_ / 10.0) };
    say SVG.serialize:
        SVG::Plot.new(
                width  => 400,
                height => 250,
                values => ([@d1], [@d2]),
                title  => 'sin(x/10), cos(x/10)',
        ).plot(:lines);


=head1 DESCRIPTION

SVG::Plot turns a set of data points (and optionally labels) into a data
structure which Carl Mäsak's module L<SVG> serializes into SVG, and displays a
bar chart of the data.

See L<http://perlgeek.de/blog-en/perl-6/svg-adventures.html> for the initial
announcement and future plans.

Note that the module itself does not depend on SVG.pm, only the examples (and
maybe in future the tests).

=head1 A WORD OF WARNING

Please note that the interface of this module is still in flux, and might
change without further notice. If you actually use it, send the author an
email to inform him, maybe he'll try to keep the interface backwards
compatible, or notify you on incompatible changes.

=head1 METHODS

=head2 new(*%options)
Constructs a L<SVG::Plot> object. You can set various attributes as options,
see their documentation below. No attribute is mandatory.

=head2 multi method plot(:$type!, :$full = True)
If the argument C<$!full> is provided, the returned data structure contains
only the body of the SVG, not the C<< <svg xmlns=...> >> header.

Each multi method renders one type of chart, and has a mandatory named
parameter with the name of the type. Currently available are C<bars>,
C<stacked-bars>, C<lines> and C<points>.

=head1 Attributes

The following attributes can be set with the C<new> constructor, and can be
queried later on (those marked with C<is rw> can also be set later on).

=head2 @.values is rw
The values to be plotted

=head2 @.labels is rw
The labels printed below the bars. Note that this must be either left empty
(in which case C<@.values.keys> is used as a default), or of the same length
as C<@.values>. To suppress printing of labels just set them all to the empty
string, C<$svg.labels = ('' xx $svg.values.elems)>.

=head2 @.links is rw
If some values of @.links are set to defined values, the corresponding bars
and labels will be turned into links

=head2 $.width
=head2 $.height

The overall size of the image (what is called the I<canvas> in SVG jargon).
SVG::Plot tries not to draw outside the canvas.

=head2 $.plot-width
=head2 $.plot-height

The size of the area to which the chart is plotted (the rest is taken up by
ticks, labels and in future probably captions). The behaviour is undefined if
C<< $.plot-width < $.width >> or C<< $.plot-height >>.

Note that if you chose C<$.plot-width> or C<$.plot-height> too big in
comparison to C<$.width> and C<$.height>, label texts and ticks might
exceed the total size, and be either clipped to or drawn outside the canvas,
depending on your SVG renderer.

=head2 $.fill-width
(Might be renamed to a more meaning name in future) For each bar in the bar
chart a certain width is allocated, but only a ratio of C<$.fill-width>  is
actually filled with a bar. Set to value between 0 and 1 to get spaces between
your bars, or to 1 if you don't  want spaces.

=head2 $.label-font-size
Font size for the axis labels

=head2 &.y-tick-step
Closure which computes the step size in which ticks and labels on the y axis
are drawn. It receives the maximal C<y> value as a single positional argument.

=head2 &.x-tick-step
Closure which computes the step size in which ticks and labels on the x axis
are drawn. It receives the maximal C<x> value as a single positional argument.

=head2 $.max-x-labels
Maximal number of plotted labels in C<x> direction. If you experience
overlapping labels you might set this to a smaller value. The default is
dependent on C<$.plot-width> and C<$.label-font-size>.

=head2 $.label-spacing

Distance between I<x> axis and labels. Also affects width of I<y> ticks and
distance of labels and I<y> ticks.

=head2 $.min-y-axis

By default the C<y> axis is scaled between the minimum and maximum y values.
Set this if you want the C<y> axis to scale off of a different lower bound.
Only has an effect if the C<$.min-y-axis> value is less then the minimum C<y>
value.

=head1 LICENSE AND COPYRIGHT

Copyright (C) 2009 by Moritz Lenz and the SVG::Plot contributors (see file
F<AUTHORS>), all rights reserved.

You may distribute, use and modify this module under the terms of the Artistic
License 2.0 as published by The Perl Foundation. See the F<LICENSE> file for
details.

The example code in the F<examples> directory and the examples from the
documentation can be used, modified and distributed freely without any
restrictions (think "public domain", except that by German law the author
can't place things into the public domain).

=head1 WARRANTY EXCLUSION

This software is provided as-is, in the hope that it is useful to somebody.
Not fitness for a particular purpose or any kind of guarantuee of
functionality is implied.

No responsibilities are taken by author to the extend allowed by applicable
law.

=end Pod

# vim: ft=perl6
